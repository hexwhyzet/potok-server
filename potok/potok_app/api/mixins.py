from potok_app.api.pictures.validators import is_valid_picture_id
from potok_app.api.profiles.validators import is_valid_profile_id


class ProfileExtractorMixin:
    def kwargs_profile(self):
        return is_valid_profile_id(self.kwargs.get('profile_id'))


class PictureExtractorMixin:
    def kwargs_picture(self):
        return is_valid_picture_id(self.kwargs.get('picture_id'))
