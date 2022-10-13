from django.db.models import signals
from django.dispatch import receiver

from potok_app.functions import token_from_id, id_from_token
from potok_app.models import Picture, Profile, Share


def create_share(sender: Profile, content):
    assert isinstance(content, Picture)
    share = Share.objects.create(sender=sender,
                                 content_object=content)
    return share


def get_token_by_share(share: Share):
    return token_from_id(share.id)


def does_share_exist(token: str):
    return Share.objects.filter(id=id_from_token(token)).exists()


def get_share_by_token(token: str):
    return Share.objects.get(id=id_from_token(token))


@receiver(signals.pre_save, sender=Share)
def like_create_receiver(sender, instance: Share, **kwargs):
    instance.content_object.shares_num += 1
    instance.content_object.save()
