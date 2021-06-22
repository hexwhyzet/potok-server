import json
from datetime import datetime

import pytz
import requests

from potok import settings
from potok_app.config import Config, Secrets
from potok_app.functions import extension_from_url
from potok_app.models import Picture, Profile, ProfileAttachment
from potok_app.services.picture import resize_and_upload_picture_to_storage
from potok_app.services.profile import add_avatar
from potok_users.models import User
import os
secrets = Secrets()
config = Config()


def downloaded_picture_is_not_reddit_gap_picture(picture_data: bytes):
    """
    Requesting deleted, banned or simply unavailable picture reddit server returns picture with the text
    'If you are looking for an image, it was probably deleted'.
    This function checks whether or not this picture is this 'gap' reddit picture.
    """
    if len(picture_data) != 1048:
        "Reddit gap picture has exactly 1048 bytes, this check is commonly faster that comparing bytes"
        return True

    with open(os.path.join(settings.STATIC_ROOT, "extra/reddit_gap_picture.png"), "rb") as gap_picture:
        return picture_data != gap_picture.read()


def pics_json_parser(pictures_json):
    """
    Current JSON Structure sent from grabber
    {
        'source_picture_id': minor id of picture in database
        'source_profile_id': minor id of profile in database
        'size': resolution of picture, example: 1280
        'date': time in UNIX format
        'url': url to picture on foreign server
        'source': example: vk
    }
    """
    print(pictures_json, file=open("temp.json", "w+"))
    pictures_data = json.loads(pictures_json)
    for picture_data in pictures_data:
        pic_profile, created = Profile.objects.get_or_create(
            minor_id=picture_data['source'] + picture_data['source_profile_id'])

        if pic_profile.user is None:
            pic_profile.user = User.objects.create_empty_user()
            pic_profile.save()

        raw_picture_data = requests.get(picture_data['url']).content

        if not downloaded_picture_is_not_reddit_gap_picture(raw_picture_data):
            continue

        picture, created = Picture.objects.get_or_create(profile=pic_profile,
                                                         minor_id=picture_data['source_picture_id'],
                                                         defaults={
                                                             "source_url": picture_data['url'],
                                                             "date": datetime.fromtimestamp(picture_data['date'],
                                                                                            pytz.timezone("UTC"))})

        if created:
            extension = extension_from_url(picture.source_url)
            resize_and_upload_picture_to_storage(
                picture=picture,
                raw_picture_data=raw_picture_data,
                extension=extension)


def profiles_json_parser(profiles_json):
    """
        Current JSON Structure sent from grabber
        {
            'source_profile_id': minor id of profile in database
            'name': not unique name of profile, example: YOUNG BIDLO BOYS
            'screen name': unique name of profile, example: youngbidlo
            'avatar_url': url to avatar on foreign server
            'avatar_size': size of avatar picture, example: 1280
            'source': example: vk
        }
        """
    profiles_data = json.loads(profiles_json)
    for profile_data in profiles_data:
        source = profile_data['source'].lower()

        profile, created = Profile.objects.update_or_create(
            minor_id=profile_data['source'] + profile_data['source_profile_id'],
            defaults={"name": profile_data['name'],
                      "screen_name": profile_data['screen_name']})

        tag = ProfileAttachment.Tag.Custom
        if source == "vk":
            tag = ProfileAttachment.Tag.VK
        if source == "reddit":
            tag = ProfileAttachment.Tag.Reddit
        if "url" in profile_data:
            ProfileAttachment.objects.update_or_create(
                tag=tag,
                profile=profile,
                defaults={
                    "url": profile_data['url']
                }
            )

        if profile.user is None:
            profile.user = User.objects.create_empty_user()
            profile.save()

        if not profile.avatars.filter(source_url=profile_data['avatar_url']).exists():
            extension = extension_from_url(profile_data['avatar_url'])
            raw_picture_data = requests.get(profile_data['avatar_url']).content
            if downloaded_picture_is_not_reddit_gap_picture(raw_picture_data):
                add_avatar(profile=profile,
                           raw_avatar_data=raw_picture_data,
                           extension=extension,
                           source_url=profile_data['avatar_url'])
