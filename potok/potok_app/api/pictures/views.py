import base64

from potok.config import Config
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from potok_app.api.http_methods import DELETE, PUT, GET
from potok_app.api.likes.views import like_content_object
from potok_app.api.mixins import FiltersMixin
from potok_app.api.paginations import MediumResultsSetPagination
from potok_app.api.pictures.permissions import GetPictureAccessPermission
from potok_app.api.pictures.serializers import PictureSerializer
from potok_app.services.picture.picture import pictures_by_filter
from potok_app.services.picture.picture_report import create_picture_report
from potok_app.services.share.share import create_share, get_token_by_share

config = Config()


class PictureViewSet(ModelViewSet, FiltersMixin):
    serializer_class = PictureSerializer
    permission_classes = []
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    pagination_class = MediumResultsSetPagination

    def get_queryset(self):
        return pictures_by_filter(**self.get_filters())

    def perform_create(self, serializer):
        base64_picture = self.request.data['base64_picture']
        picture_bytes = base64.b64decode(base64_picture)
        profile = self.get_kwargs_profile()
        extension = self.request.data['extension']
        serializer.save(profile=profile, picture_bytes=picture_bytes, extension=extension)

    @action(detail=True, methods=[PUT, DELETE], permission_classes=[GetPictureAccessPermission])
    def like(self, request, *args, **kwargs):
        picture = self.get_object()
        like_content_object(self.request, picture)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=[PUT], permission_classes=[GetPictureAccessPermission])
    def report(self, request, *args, **kwargs):
        picture = self.get_object()
        user_profile = self.request.user.profile
        create_picture_report(picture, user_profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=[GET], serializer_class=[GetPictureAccessPermission])
    def share(self, request, *args, **kwargs):
        picture = self.get_object()
        user_profile = self.request.user.profile
        share = create_share(user_profile, picture)
        return Response({"url": f"{config['main_server_ip']}/share/{get_token_by_share(share)}"},
                        status=status.HTTP_200_OK)
