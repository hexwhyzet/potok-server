from rest_framework.exceptions import ParseError

from potok_app.api.pictures.validators import is_valid_picture_id
from potok_app.api.profiles.validators import is_valid_profile_id
from potok_app.services.picture.picture import does_picture_exist
from potok_app.services.profile.profile import does_profile_exist

PROFILE_ID = 'profile_id'
PICTURE_ID = 'picture_id'


class FiltersMixin:
    def get_filters(self):
        filters = {}
        if PROFILE_ID in self.kwargs and does_profile_exist(self.kwargs.get('profile_id')):
            filters[PROFILE_ID] = self.kwargs.get('profile_id')
        if PICTURE_ID in self.kwargs and does_picture_exist(self.kwargs.get('picture_id')):
            filters[PROFILE_ID] = self.kwargs.get('profile_id')
        return filters

    def get_kwargs_profile(self):
        if PROFILE_ID not in self.kwargs:
            raise ParseError()
        return is_valid_profile_id(self.kwargs.get('profile_id'))

    def get_kwargs_picture(self):
        if PICTURE_ID not in self.kwargs:
            raise ParseError()
        return is_valid_picture_id(self.kwargs.get('profile_id'))
