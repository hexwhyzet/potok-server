import json
from datetime import datetime
from random import randint

import boto3
import pytz
import requests
from django.contrib.auth.models import User

from .config import Config, Secrets
from .models import Picture, Profile

secrets = Secrets()
config = Config()


def pics_json_parser(json_pics_data):
    pics_data = json.loads(json_pics_data)
    for pic_data in pics_data:
        source_url = pic_data['photo']['link']
        pic_minor_id = pic_data['post_id']
        pic_profile_minor_id = 'vk' + str(abs(int(pic_data['source_id'])))
        pic_profile, _ = Profile.objects.get_or_create(
            minor_id=pic_profile_minor_id,
            defaults={"user": User.objects.create_user(str(randint(1, 100000000000)))})
        if not Picture.objects.filter(minor_id=pic_minor_id, profile__minor_id=pic_profile).exists():
            pic = Picture.create(profile=pic_profile,
                                 source_url=source_url,
                                 minor_id=pic_minor_id,
                                 res=pic_data['photo']['size'],
                                 date=datetime.fromtimestamp(pic_data['date'], pytz.timezone("UTC")))
            pic_url = download_picture_to_bucket(source_url, f"{pic.profile.id}/{pic.id}.jpg")
            pic.url = pic_url
            pic.save()


def profiles_json_parser(clubs_data):
    profiles_data = json.loads(clubs_data)
    for profile_data in profiles_data:
        minor_id = "vk" + str(abs(int(profile_data['source_id'])))
        profile, _ = Profile.objects.get_or_create(
            minor_id=minor_id,
            defaults={"user": User.objects.create_user(str(randint(1, 100000000000)))})
        pic_path = download_picture_to_bucket(profile_data['photo_url'], f"{profile.id}/avatars/avatar.jpg")
        profile.name = profile_data['name']
        profile.screen_name = profile_data['screen_name']
        profile.avatar_url = pic_path
        profile.save()


def download_picture_to_bucket(source_url, bucket_path):
    response = requests.get(source_url)
    if response.status_code == 200:
        s3 = boto3.resource(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
        bucket = s3.Bucket('void-bucket')
        data = response.content
        image_path = bucket_path
        bucket.put_object(Key=image_path, Body=data)
        return "/" + image_path

# def download_picture_locally(url, pic_name, source_id):
#     response = requests.get(url)
#     if response.status_code == 200:
#         Path(f"media/{source_id}").mkdir(parents=True, exist_ok=True)
#         pic_path = f"media/{source_id}/{str(pic_name)}.png"
#         with open(pic_path, 'wb+') as out_file:
#             out_file.write(response.content)
#         return pic_path
