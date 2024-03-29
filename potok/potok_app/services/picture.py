import logging
from datetime import datetime

import pytz
import requests

from potok_app.config import Secrets, Config
from potok_app.functions import id_gen, extension_from_url
from potok_app.models import Picture, Profile, Session, Like, PictureData, PictureReport
from potok_app.object_storage_api import upload_picture
from potok_app.picture_resizer import resize_and_compress

secrets = Secrets()
config = Config()

logger = logging.getLogger(__name__)


def picture_by_id(picture_id):
    return Picture.objects.get(id=picture_id)


def subscription_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).exclude(profile__in=profile.blocked_profiles.all()).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.sub_pics.add(picture)
        session.save()
    return pictures


def feed_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.exclude(profile__is_public=False).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).exclude(profile__in=profile.blocked_profiles.all()).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.feed_pics.add(picture)
        session.save()
    return pictures


def profile_pictures(profile_id, number=10, offset=0):
    pictures = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:offset + number]
    return pictures


def liked_pictures(profile_id, number=10, offset=0):
    pictures = list(
        map(lambda x: x.picture, Like.objects.filter(profile=profile_id).order_by('-date')[offset:offset + number]))
    return pictures


def add_picture(profile, picture_data, extension, link):
    picture = Picture.create(profile=profile,
                             link_url=link,
                             date=datetime.fromtimestamp(datetime.now().timestamp(), pytz.timezone("UTC")))
    resize_and_upload_picture_to_storage(
        picture=picture,
        raw_picture_data=picture_data,
        extension=extension)


def delete_picture(picture: Picture):
    picture.delete()


def resize_and_upload_picture_to_storage(picture, raw_picture_data, extension, widths=None):
    for res, resized_picture in resize_and_compress(raw_picture_data, extension, widths).items():
        url = upload_picture(resized_picture, f'{config["image_server_directory"]}/{id_gen(50)}.{extension}')
        picture_data, _ = PictureData.objects.get_or_create(picture=picture, res=res, url=url)


def picture_can_be_deleted_by_user(user_profile: Profile, picture: Picture):
    return picture.profile == user_profile


def get_resolution_url(picture: Picture, res: int):
    if not picture.picture_data.filter(res=res).exists():
        logger.warning(f"Picture id: {picture.id} was NOT found with resolution {res}")
        resize_and_upload_picture_to_storage(picture, requests.get(picture.source_url).content,
                                             extension_from_url(picture.source_url), [res])

    return picture.picture_data.get(res=res).url


def add_report(profile: Profile, picture: Picture):
    PictureReport.objects.create(profile=profile, picture=picture)


def high_resolution_url(picture: Picture):
    return get_resolution_url(picture, 1280)


def mid_resolution_url(picture: Picture):
    return get_resolution_url(picture, 640)


def low_resolution_url(picture: Picture):
    return get_resolution_url(picture, 320)
