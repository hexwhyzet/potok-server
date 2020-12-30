import json
from datetime import datetime
from random import randint

import boto3
import pytz
import requests
from django.contrib.auth.models import User

from potok_app.config import Config, Secrets
from potok_app.models import Picture, Profile

secrets = Secrets()
config = Config()


def pics_json_parser(json_pics_data):
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
    pics_data = json.loads(json_pics_data)
    for pic_data in pics_data:
        source_url = pic_data['url']
        pic_minor_id = pic_data['source_picture_id']
        pic_profile_minor_id = pic_data['source'] + str(abs(int(pic_data['source_profile_id'])))
        pic_profile, _ = Profile.objects.get_or_create(
            minor_id=pic_profile_minor_id,
            defaults={"user": User.objects.create_user(str(randint(1, 100000000000)))})
        if not Picture.objects.filter(minor_id=pic_minor_id, profile=pic_profile).exists():
            pic = Picture.create(profile=pic_profile,
                                 source_url=source_url,
                                 minor_id=pic_minor_id,
                                 res=pic_data['size'],
                                 date=datetime.fromtimestamp(pic_data['date'], pytz.timezone("UTC")))
            pic_url = upload_picture_to_bucket(requests.get(source_url).content, f"{pic.profile.id}/{pic.id}.jpg")
            pic.url = pic_url
            pic.save()


def profiles_json_parser(clubs_data):
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
    profiles_data = json.loads(clubs_data)
    for profile_data in profiles_data:
        minor_id = profile_data['source'] + str(abs(int(profile_data['source_profile_id'])))
        profile, _ = Profile.objects.get_or_create(
            minor_id=minor_id,
            defaults={"user": User.objects.create_user(str(randint(1, 100000000000)))})
        pic_path = upload_picture_to_bucket(requests.get(profile_data['avatar_url']).content,
                                            f"{profile.id}/avatars/avatar.jpg")
        profile.name = profile_data['name']
        profile.screen_name = profile_data['screen_name']
        profile.avatar_url = pic_path
        profile.save()


def pic_upload(picture_data, profile, extension):
    picture = Picture.create(profile=profile,
                             date=datetime.fromtimestamp(datetime.now().timestamp(), pytz.timezone("UTC")))
    picture_url = upload_picture_to_bucket(picture_data, f"{profile.id}/{picture.id}.{extension}")
    picture.url = picture_url
    picture.save()


def upload_picture_to_bucket(picture_data, bucket_path):
    s3 = boto3.resource(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
    bucket = s3.Bucket('void-bucket')
    bucket.put_object(Key=bucket_path, Body=picture_data)
    return "/" + bucket_path
