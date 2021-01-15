from io import BytesIO

import boto3
from PIL import Image

QUALITY = 85

WIDTH = [1280, 640, 320, 160]


def resize_and_compress(image_raw, _format):
    _format = 'JPEG' if _format.lower() == 'jpg' else _format.upper()

    images_list = []
    images_outputs = [BytesIO() for _ in range(len(WIDTH))]
    image = Image.open(BytesIO(image_raw))
    for width in WIDTH:
        height = int(image.size[1] * (width / image.size[0]))
        images_list.append(image.resize((width, height), Image.ANTIALIAS))
    answer = {}
    for i in range(len(images_list)):
        images_list[i].save(images_outputs[i], format=_format, quality=QUALITY, optimize=True)
        images_outputs[i].seek(0)
        answer[WIDTH[i]] = images_outputs[i]
    return answer


def upload_picture_to_bucket(picture_data, bucket_path):
    s3 = boto3.resource(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
    bucket = s3.Bucket('void-bucket')
    bucket.put_object(Key=bucket_path, Body=picture_data)
    return "/" + bucket_path


if __name__ == '__main__':
    pass
