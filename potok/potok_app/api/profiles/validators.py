from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from potok_app.services.profile.profile import profile_by_id


def is_valid_profile_id(profile_id):
    try:
        profile = profile_by_id(profile_id)
        return profile
    except ObjectDoesNotExist:
        raise NotFound()
