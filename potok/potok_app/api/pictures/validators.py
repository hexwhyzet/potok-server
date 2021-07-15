from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.exceptions import ValidationError

from potok_app.services.picture import picture_by_id


def is_valid_picture_id(picture_id):
    try:
        picture = picture_by_id(picture_id)
        return picture
    except ObjectDoesNotExist:
        raise ValidationError("Picture with given `picture_id` does not exist")
    except MultipleObjectsReturned:
        raise ValidationError("Picture with given `picture_id` is duplicated")