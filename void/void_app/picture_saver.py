import requests
import json
from .models import Meme


def meme_json_parser(meme_data):
    meme_data = json.loads(meme_data)
    for meme in meme_data:
        picture_url = meme['photo']['link']
        pic_name = meme['post_id']
        pic_path = save_picture_from_link(picture_url, pic_name)
        Meme.objects.create_meme(meme_data, pic_path)


def save_picture_from_link(url, pic_name):
    response = requests.get(url)
    if response.status_code == 200:
        pic_path = 'saved_pics/' + str(pic_name) + '.png'
        with open(pic_path, 'wb') as out_file:
            out_file.write(response.content)
        return pic_path


with open('meme_data_json.json', 'r') as json_cont:
    cont = json_cont.read()
    meme_json_parser(cont)
