from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.exceptions import ValidationError

from potok_app.services.actions import comment_by_id
from potok_app.services.picture import picture_by_id


def is_valid_comment_id(picture_id):
    try:
        comment = comment_by_id(picture_id)
        return comment
    except ObjectDoesNotExist:
        raise ValidationError("Picture with given `picture_id` does not exist")
    except MultipleObjectsReturned:
        raise ValidationError("Picture with given `picture_id` is duplicated")