from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

from potok_app.api.http_methods import *
from potok_app.api.pictures.permissions import GetPictureAccessPermission
from potok_app.api.pictures.validators import is_valid_picture_id
from potok_app.api.profiles.permissions import IsProfileUsers


class CommentAccessPermission(permissions.BasePermission):
    """
    Object-level permission

    - GET comment for
        - users that have access to the profile under whose picture the comment was left
        - user that owns profile that posted the comment

    - DELETE comment for
        - user that owns profile under whose picture the comment was left
        - user that owns profile that posted the comment
        - admins

    - PATCH comment for
        - user that own profile that posted the comment

    - POST comment for
        - users that have GET access to picture under which comment is going to be left

    Assumes the comment model instance has an `picture` and `profile` attributes.
    """

    def has_permission(self, request, view):

        if view.action == 'list':
            return ListCommentAccessPermission().has_permission(request, view)

        if request.method == POST:
            return PostCommentAccessPermission().has_permission(request, view)

        return True

    def has_object_permission(self, request, view, comment_obj):

        if request.method == GET:
            return GetCommentAccessPermission().has_object_permission(request, view, comment_obj)

        if request.method == DELETE:
            return DeleteCommentAccessPermission().has_object_permission(request, view, comment_obj)

        if request.method == PATCH:
            return PatchCommentAccessPermission().has_object_permission(request, view, comment_obj)

        return False


class ListCommentAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        picture = is_valid_picture_id(view.kwargs.get('picture_id'))
        return GetPictureAccessPermission().has_object_permission(request, view, picture)


class PostCommentAccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        picture = is_valid_picture_id(view.kwargs.get('picture_id'))
        return GetPictureAccessPermission().has_object_permission(request, view, picture)


class GetCommentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, comment_obj):
        return IsProfileUsers().has_object_permission(request, view, comment_obj.picture.profile) \
               or GetPictureAccessPermission().has_object_permission(request, view, comment_obj.picture)


class DeleteCommentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, comment_obj):
        return IsAdminUser().has_permission(request, view) \
               or IsProfileUsers().has_object_permission(request, view, comment_obj.picture.profile) \
               or IsProfileUsers().has_object_permission(request, view, comment_obj.profile)


class PatchCommentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, comment_obj):
        return IsProfileUsers().has_object_permission(request, view, comment_obj.picture.profile)
