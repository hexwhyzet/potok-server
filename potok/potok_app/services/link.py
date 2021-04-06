from django.contrib.contenttypes.models import ContentType

from potok_app.functions import token_from_id, id_from_token
from potok_app.models import Profile, Link, Picture


# def create_link(sender: Profile, content):
#     if isinstance(content, Picture) or isinstance(content, Profile):
#
#         if isinstance(content, Picture) and not Link.objects.filter(sender=sender, content=content).exists():
#
#         link = Link.objects.create(sender=sender, content_type=ContentType.objects.get_for_model(content),
#                                    content=content)
#         return link
#     else:
#         return ValueError("Content not instance of Picture or Profile")


def create_picture_link(sender: Profile, content: Picture):
    link = Link.objects.create(sender=sender, content_type=ContentType.objects.get_for_model(content),
                               content=content)
    content.shares_num += 1
    content.save()
    return link


def share_token_by_link(link: Link):
    return token_from_id(link.id)


def link_by_share_token(share_token: str):
    return Link.objects.get(id=id_from_token(share_token))
