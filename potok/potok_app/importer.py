import json
from datetime import datetime
from random import randint

import pytz
import requests

from potok_app.config import Config, Secrets
from potok_app.functions import extension_from_url
from potok_app.models import Picture, Profile
from potok_app.services.picture import resize_and_upload_picture_to_storage
from potok_app.services.profile import add_avatar
from potok_users.models import User

secrets = Secrets()
config = Config()


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
    pictures_data = json.loads(pictures_json)
    for picture_data in pictures_data:
        pic_profile, created = Profile.objects.get_or_create(
            minor_id=picture_data['source'] + str(abs(int(picture_data['source_profile_id']))))

        if created:
            pic_profile.user = User.objects.create_user(str(randint(1, 100000000000)))

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
                raw_picture_data=requests.get(picture.source_url).content,
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
        profile, created = Profile.objects.update_or_create(
            minor_id=profile_data['source'] + str(abs(int(profile_data['source_profile_id']))),
            defaults={"name": profile_data['name'],
                      "screen_name": profile_data['screen_name']})

        if created:
            profile.user = User.objects.create_user(str(randint(1, 100000000000)))

        if not profile.avatars.filter(source_url=profile_data['avatar_url']).exists():
            extension = extension_from_url(profile_data['avatar_url'])
            add_avatar(profile=profile,
                       raw_avatar_data=requests.get(profile_data['avatar_url']).content,
                       extension=extension,
                       res=profile_data['avatar_size'],
                       source_url=profile_data['avatar_url'])
