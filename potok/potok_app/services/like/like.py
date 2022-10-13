from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

from potok_app.models import Profile, Like


def does_like_exist(content_object: models.Model, profile: Profile):
    return Like.objects.filter(
        object_id=content_object.id,
        content_type=ContentType.objects.get_for_model(content_object),
        profile=profile,
    ).exists()


def get_like(content_object: models.Model, profile: Profile):
    return Like.objects.get(
        object_id=content_object.id,
        content_type=ContentType.objects.get_for_model(content_object),
        profile=profile,
    )


def delete_like(content_object: models.Model, profile: Profile):
    return get_like(content_object, profile).delete()


def create_like(content_object: models.Model, profile: Profile):
    return Like.objects.create(
        content_object=content_object,
        profile=profile,
    )


@receiver(signals.pre_delete, sender=Like)
def like_delete_receiver(sender, instance: Like, **kwargs):
    instance.content_object.likes_num -= 1
    instance.content_object.save()


@receiver(signals.pre_save, sender=Like)
def like_create_receiver(sender, instance: Like, **kwargs):
    instance.content_object.likes_num += 1
    instance.content_object.save()
