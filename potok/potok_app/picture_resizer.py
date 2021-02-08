from io import BytesIO

import boto3
from PIL import Image

from .config import Config

QUALITY = 85

WIDTHS = (1280, 640, 320, 160)

config = Config()


def resize_and_compress(image_raw, _format, widths):
    if widths is None:
        widths = WIDTHS

    _format = 'JPEG' if _format.lower() == 'jpg' else _format.upper()

    images_list = []
    images_outputs = [BytesIO() for _ in range(len(widths))]
    image = Image.open(BytesIO(image_raw))
    for width in widths:
        height = int(image.size[1] * (width / image.size[0]))
        images_list.append(image.resize((width, height), Image.ANTIALIAS))
    answer = {}
    for i in range(len(images_list)):
        images_list[i].save(images_outputs[i], format=_format, quality=QUALITY, optimize=True)
        images_outputs[i].seek(0)
        answer[widths[i]] = images_outputs[i]
    return answer


def upload_picture_to_bucket(picture_data, bucket_path):
    s3 = boto3.resource(service_name='s3', endpoint_url=config["image_server_url"])
    bucket = s3.Bucket(config["image_server_bucket"])
    bucket.put_object(Key=bucket_path, Body=picture_data)
    return "/" + bucket_path


if __name__ == '__main__':
    pass
