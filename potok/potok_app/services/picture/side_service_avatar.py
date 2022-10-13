from potok_app.functions import extension_from_url
from potok_app.models import Profile, Avatar
from potok_app.services.picture.picture_data import create_picture_data_of_all_sizes


def does_side_service_avatar_exist(profile: Profile, source_url: str):
    return Avatar.objects.filter(profile=profile, source_url=source_url).exists()


def get_or_create_side_service_avatar(profile: Profile, source_url: str, picture_bytes):
    avatar, created = Avatar.objects.get_or_create(profile=profile, source_url=source_url)
    if created:
        create_picture_data_of_all_sizes(avatar, picture_bytes, extension_from_url(source_url))
    return avatar
