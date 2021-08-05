from django.contrib.contenttypes.models import ContentType

from potok_app.functions import token_from_id, id_from_token
from potok_app.models import Picture, Profile, Share


def create_share(sender: Profile, content):
    assert isinstance(content, Picture)
    share = Share.objects.create(sender=sender,
                                 content_type=ContentType.objects.get_for_model(content),
                                 content=content)
    content.shares_num += 1
    content.save()
    return share


def get_token_by_share(share: Share):
    return token_from_id(share.id)


def get_share_by_token(token: str):
    return Share.objects.get(id=id_from_token(token))
