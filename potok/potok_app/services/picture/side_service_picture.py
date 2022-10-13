import datetime

from potok_app.functions import extension_from_url
from potok_app.models import Profile, Picture
from potok_app.services.picture.picture_data import create_picture_data_of_all_sizes


def does_side_service_picture_exists(profile: Profile, minor_id: str):
    return Picture.objects.filter(profile=profile, minor_id=minor_id).exists()


def get_or_create_side_service_picture(profile: Profile, minor_id: str, source_url: str, picture_bytes,
                                       date: datetime.date):
    picture, created = Picture.objects.get_or_create(profile=profile, minor_id=minor_id,
                                                     defaults={
                                                         "source_url": source_url,
                                                     })
    picture.date = date  # Date is set to auto_add_now so date in defaults is overwritten by now timestamp
    picture.save()
    if created:
        create_picture_data_of_all_sizes(picture, picture_bytes, extension_from_url(source_url))
    return picture
