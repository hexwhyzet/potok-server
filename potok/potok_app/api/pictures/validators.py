from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from potok_app.services.picture.picture import picture_by_id


def is_valid_picture_id(picture_id):
    try:
        picture = picture_by_id(picture_id)
        return picture
    except ObjectDoesNotExist:
        raise NotFound()
