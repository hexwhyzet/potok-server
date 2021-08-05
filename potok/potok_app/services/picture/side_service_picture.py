import datetime

from potok_app.models import Profile, Picture
from potok_app.services.picture.picture_data import create_picture_data_of_all_sizes


def does_side_service_picture_exists(profile: Profile, minor_id: str):
    return Picture.objects.filter(profile=profile, minor_id=minor_id).exists()


def get_or_create_side_service_picture(profile: Profile, minor_id: str, source_url: str, picture_bytes, extension,
                                       date: datetime.date):
    picture, created = Picture.objects.get_or_create(profile=profile, minor_id=minor_id,
                                                     defaults={
                                                         "source_url": source_url,
                                                         "date": date,
                                                     })
    if created:
        create_picture_data_of_all_sizes(picture, picture_bytes, extension)
    return picture
