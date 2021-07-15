from django.http import JsonResponse
from rest_framework import generics
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.views import APIView

from potok_app.api.comments.permissions import CommentAccessPermission
from potok_app.api.comments.serializers import CommentSerializer
from potok_app.api.comments.validators import is_valid_comment_id
from potok_app.api.pictures.validators import is_valid_picture_id
from potok_app.api.templates import CustomListAPIView
from potok_app.models import Comment
from potok_app.services.actions import comments_of_picture


class CommentList(CustomListAPIView):
    model = Comment
    serializer_class = CommentSerializer
    permission_classes = [CommentAccessPermission]

    def get_queryset(self):
        picture_id = self.request.query_params.get('picture_id')
        picture = is_valid_picture_id(picture_id)
        count, offset = self.extract_count(), self.extract_offset()
        comments_queryset = comments_of_picture(picture, count, offset)
        return comments_queryset


class CommentView(GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CommentAccessPermission]

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     obj = get_object_or_404(queryset, **filter_kwargs)
    #     self.check_object_permissions(self.request, obj)
    #     return obj

    def get(self, request):
        comment_id = self.request.query_params.get('comment_id')
        comment = is_valid_comment_id(comment_id)
        serializer = self.serializer_class(comment, request.data)
        serializer.is_valid(raise_exception=True)

        self.get_object()

        self.check_object_permissions()

        return JsonResponse(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse()

    def delete(self, request):
        comment_id = self.request.query_params.get('comment_id')
        comment = is_valid_comment_id(comment_id)
        comment.delete()
        serializer = self.serializer_class(comment, request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse()
