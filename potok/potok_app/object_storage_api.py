import boto3

from potok_app.config import Secrets, Config

secrets = Secrets()
config = Config()


def upload_picture_bytes(picture_data, bucket_path):
    s3 = boto3.resource(service_name='s3', endpoint_url=config['image_server_url'])
    bucket = s3.Bucket(config['image_server_bucket'])
    bucket.put_object(Key=bucket_path, Body=picture_data)
    return '/' + bucket_path


def get_bucket_url():
    return config['image_server_url'] + '/' + config['image_server_bucket']
