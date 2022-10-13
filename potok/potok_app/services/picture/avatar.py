from django.db.models import signals
from django.dispatch import receiver

from potok_app.config import Config
from potok_app.models import Profile, Avatar
from potok_app.services.picture.picture_data import create_picture_data_of_all_sizes, \
    delete_picture_data_by_content_object

config = Config()


def available_avatars():
    return Avatar.objects.all()


def avatars_by_profile(profile: Profile):
    return Avatar.objects.filter(profile=profile)


def create_avatar(profile: Profile, picture_bytes, extension: str):
    avatar = Avatar.objects.create(profile=profile)
    create_picture_data_of_all_sizes(avatar, picture_bytes, extension)
    return avatar


def get_gap_avatar():
    return Avatar.objects.get(id=config['default_avatar_id'])


def get_current_avatar_or_gap_avatar(profile: Profile):
    if profile.avatars.count() == 0:
        return get_gap_avatar()
    return profile.avatars.last()


@receiver(signals.pre_delete, sender=Avatar)
def cascade_delete(sender, instance, **kwargs):
    delete_picture_data_by_content_object(instance)
