import json
from pathlib import Path

import boto3
import requests

from .config import Config, Secrets
from .models import Meme, Club

secrets = Secrets()
config = Config()


def meme_json_parser(meme_data):
    meme_data = json.loads(meme_data)
    for meme in meme_data:
        picture_url = meme['photo']['link']
        pic_name = meme['post_id']
        source_id = meme['source_id']
        club, _ = Club.objects.get_or_create(id=source_id)
        pic_path = "/" + download_picture_to_bucket(picture_url, pic_name, source_id)
        Meme.objects.create_meme(meme, pic_path, club).save()


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
