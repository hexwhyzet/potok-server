import json
from pathlib import Path

import boto3
import requests

from .config import Config, Secrets
from .models import Meme, Club

secrets = Secrets()
config = Config()


def meme_json_parser(memes_data):
    memes_data = json.loads(memes_data)
    for meme_data in memes_data:
        picture_url = meme_data['photo']['link']
        pic_name = meme_data['post_id']
        source_id = abs(meme_data['source_id'])
        club, _ = Club.objects.get_or_create(id=source_id)

        if not Meme.objects.filter(picture_url=f"/{source_id}/{pic_name}").exists():
            pic_path = "/" + download_picture_to_bucket(picture_url, pic_name, source_id)
            Meme.objects.create_meme(meme_data, pic_path, club).save()


def club_json_parser(clubs_data):
    clubs_data = json.loads(clubs_data)
    for club_data in clubs_data:
        source_id = club_data['source_id']
        club, _ = Club.objects.get_or_create(id=source_id)
        pic_path = "/" + download_picture_to_bucket(club_data['photo_url'], "profile_picture", source_id)
        club.profile_picture_url = pic_path
        club.name = club_data['name']
        club.screen_name = club_data['screen_name']
        club.save()


def download_picture_to_bucket(url, pic_name, source_id):
    response = requests.get(url)
    if response.status_code == 200:
        s3 = boto3.resource(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
        bucket = s3.Bucket('void-bucket')
        data = response.content
        image_path = f"{source_id}/{str(pic_name)}.png"
        bucket.put_object(Key=image_path, Body=data)
        return image_path


def download_picture_locally(url, pic_name, source_id):
    response = requests.get(url)
    if response.status_code == 200:
        Path(f"media/{source_id}").mkdir(parents=True, exist_ok=True)
        pic_path = f"media/{source_id}/{str(pic_name)}.png"
        with open(pic_path, 'wb+') as out_file:
            out_file.write(response.content)
        return pic_path
