import base64

from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from potok_app.api.avatars.serializers import AvatarSerializer
from potok_app.api.http_methods import GET
from potok_app.api.mixins import FiltersMixin
from potok_app.api.paginations import SmallResultsSetPagination
from potok_app.api.profiles.validators import is_valid_profile_id
from potok_app.services.picture.avatar import avatars_by_profile, get_current_avatar_or_gap_avatar


class AvatarViewSet(ModelViewSet, FiltersMixin):
    serializer_class = AvatarSerializer
    permission_classes = []
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return avatars_by_profile(profile=is_valid_profile_id(self.kwargs['profile_id']))

    def perform_create(self, serializer):
        base64_picture = self.request.data['base64_picture']
        picture_bytes = base64.b64decode(base64_picture)
        profile = self.get_kwargs_profile()
        extension = self.request.data['extension']
        serializer.save(profile=profile, picture_bytes=picture_bytes, extension=extension)

    @action(detail=False, methods=[GET])
    def current(self, request, *args, **kwargs):
        profile = self.get_kwargs_profile()
        if profile.avatars.count() == 0:
            raise NotFound()
        current_avatar = get_current_avatar_or_gap_avatar(profile)
        serializer = self.serializer_class(current_avatar)
        return Response(serializer.data)
