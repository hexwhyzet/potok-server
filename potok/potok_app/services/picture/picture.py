from django.db.models import signals
from django.dispatch import receiver

from potok_app.models import Picture, Profile
from potok_app.services.picture.picture_data import create_picture_data_of_all_sizes, \
    delete_picture_data_by_content_object


def available_pictures():
    return Picture.objects.all()


def does_picture_exist(picture_id):
    return Picture.objects.filter(id=picture_id).exists()


def picture_by_id(picture_id):
    return Picture.objects.get(id=picture_id)


def pictures_by_profile(profile: Profile):
    return Picture.objects.filter(profile=profile).order_by('-date')


def pictures_by_filter(**kwarg):
    return Picture.objects.filter(**kwarg).order_by('-date')


def create_picture(profile: Profile, picture_bytes, extension: str, text: str = None, link_url: str = None):
    picture = Picture.objects.create(profile=profile, text=text, link_url=link_url)
    create_picture_data_of_all_sizes(picture, picture_bytes, extension)
    return picture


@receiver(signals.pre_delete, sender=Picture)
def cascade_delete(sender, instance, **kwargs):
    delete_picture_data_by_content_object(instance)
