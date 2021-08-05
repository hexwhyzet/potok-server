from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from potok_app.api.comments.permissions import GetCommentAccessPermission, CommentAccessPermission
from potok_app.api.comments.serializers import CommentSerializer
from potok_app.api.http_methods import DELETE, PUT
from potok_app.api.likes.views import like_content_object
from potok_app.api.paginations import StandardResultsSetPagination
from potok_app.api.pictures.validators import is_valid_picture_id
from potok_app.services.comment.comment import comments_by_picture


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CommentAccessPermission]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return comments_by_picture(picture=is_valid_picture_id(self.kwargs['picture_id']))

    def perform_create(self, serializer):
        picture = is_valid_picture_id(self.kwargs['picture_id'])
        profile = self.request.user.profile
        serializer.save(profile=profile, picture=picture)

    @action(detail=True, methods=[DELETE, PUT], permission_classes=[IsAuthenticated, GetCommentAccessPermission])
    def like(self, request, **kwargs):
        comment = self.get_object()
        like_content_object(self.request, comment)
        return Response(status=status.HTTP_204_NO_CONTENT)
