import json
import os

import requests

from potok import settings
from potok_app.config import Config, Secrets
from potok_app.functions import extension_from_url, timestamp_to_date
from potok_app.models import ProfileAttachment
from potok_app.services.picture.side_service_avatar import get_or_create_side_service_avatar, \
    does_side_service_avatar_exist
from potok_app.services.picture.side_service_picture import get_or_create_side_service_picture, \
    does_side_service_picture_exists
from potok_app.services.profile.profile_attachment import update_or_create_profile_attachment
from potok_app.services.profile.side_service_profile import get_or_create_side_service_profile, \
    update_or_create_side_service_profile
from potok_users.models import User

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

    with open(os.path.join(settings.STATIC_ROOT, 'extra/reddit_gap_picture.png'), 'rb') as gap_picture:
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
    side_server_pictures_dict = json.loads(pictures_json)
    for side_server_picture_dict in side_server_pictures_dict:
        pic_profile, _ = get_or_create_side_service_profile(
            minor_id=side_server_picture_dict['source'] + side_server_picture_dict['source_profile_id'])

        if pic_profile.user is None:
            pic_profile.user = User.objects.create_empty_user()
            pic_profile.save()

        if not does_side_service_picture_exists(pic_profile, side_server_picture_dict['source_picture_id']):

            picture_bytes = requests.get(side_server_picture_dict['url']).content

            if not downloaded_picture_is_not_reddit_gap_picture(picture_bytes):
                continue

            date = timestamp_to_date(side_server_picture_dict['date'])

            get_or_create_side_service_picture(profile=pic_profile,
                                               minor_id=side_server_picture_dict[
                                                   'source_picture_id'],
                                               source_url=side_server_picture_dict['url'],
                                               picture_bytes=picture_bytes,
                                               extension=side_server_picture_dict['source_url'],
                                               date=date)


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
    side_service_profiles_dict = json.loads(profiles_json)
    for side_service_profile_dict in side_service_profiles_dict:
        source = side_service_profile_dict['source'].lower()

        profile, _ = update_or_create_side_service_profile(
            minor_id=side_service_profile_dict['source'] + side_service_profile_dict['source_profile_id'],
            name=side_service_profile_dict['name'],
            screen_name=side_service_profile_dict['screen_name'])

        tag = ProfileAttachment.Tag.Custom
        if source == 'vk':
            tag = ProfileAttachment.Tag.VK
        if source == 'reddit':
            tag = ProfileAttachment.Tag.Reddit
        if 'url' in side_service_profile_dict:
            update_or_create_profile_attachment(
                tag=tag,
                profile=profile,
                url=side_service_profile_dict['url'])

        if profile.user is None:
            profile.user = User.objects.create_empty_user()
            profile.save()

        avatar_url = side_service_profile_dict['avatar_url']

        if not does_side_service_avatar_exist(profile, avatar_url):
            extension = extension_from_url(avatar_url)
            picture_bytes = requests.get(avatar_url).content
            if downloaded_picture_is_not_reddit_gap_picture(picture_bytes):
                get_or_create_side_service_avatar(profile=profile,
                                                  source_url=avatar_url,
                                                  picture_bytes=picture_bytes,
                                                  extension=extension)
