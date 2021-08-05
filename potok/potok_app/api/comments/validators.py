from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from potok_app.services.comment.comment import comment_by_id


def is_valid_comment_id(comment_id):
    try:
        comment = comment_by_id(comment_id)
        return comment
    except ObjectDoesNotExist:
        raise NotFound()
