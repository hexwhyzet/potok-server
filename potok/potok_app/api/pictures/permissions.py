from rest_framework import permissions

from potok_app.api.http_methods import GET, DELETE, PATCH, POST
from potok_app.api.profiles.permissions import GetProfileContentAccessPermission, \
    DeleteProfileContentAccessPermission, PatchProfileContentAccessPermission, IsProfileUsers
from potok_app.api.profiles.validators import is_valid_profile_id


class PictureAccessPermission(permissions.BasePermission):
    """
    Object-level permission

    - GET/DELETE/PATCH same as access permission to profile that posted picture

    - POST always allowed
    """

    def has_permission(self, request, view):
        if request.method == POST:
            return PostPictureAccessPermission().has_permission(request, view)

    def has_object_permission(self, request, view, picture_obj):
        if request.method == GET:
            return GetPictureAccessPermission().has_object_permission(request, view, picture_obj)

        if request.method == DELETE:
            return DeletePictureAccessPermission().has_object_permission(request, view, picture_obj)

        if request.method == PATCH:
            return PatchPictureAccessPermission().has_object_permission(request, view, picture_obj)

        return False


class PostPictureAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        pictures_profile = is_valid_profile_id(view.kwargs['profile_id'])
        return IsProfileUsers().has_object_permission(request, view, pictures_profile)


class GetPictureAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, picture_obj):
        return GetProfileContentAccessPermission().has_object_permission(request, view, picture_obj.profile)


class DeletePictureAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, picture_obj):
        return DeleteProfileContentAccessPermission().has_object_permission(request, view, picture_obj.profile)


class PatchPictureAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, picture_obj):
        return PatchProfileContentAccessPermission().has_object_permission(request, view, picture_obj.profile)
