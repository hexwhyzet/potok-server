import json

import requests

from .config import Config, Secrets
from .models import Meme

secrets = Secrets()
config = Config()


def meme_json_parser(meme_data):
    meme_data = json.loads(meme_data)
    for meme in meme_data:
        picture_url = meme['photo']['link']
        pic_name = meme['post_id']
        pic_path = save_picture_from_link(picture_url, pic_name)
        pic_path = pic_path[6:]
        Meme.objects.create_meme(meme, pic_path).save()


def save_picture_from_link(url, pic_name):
    response = requests.get(url)
    if response.status_code == 200:
        pic_path = 'media/saved_pics/' + str(pic_name) + '.png'
        with open(pic_path, 'wb') as out_file:
            out_file.write(response.content)
        return pic_path
