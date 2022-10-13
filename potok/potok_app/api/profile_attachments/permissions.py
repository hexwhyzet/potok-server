from rest_framework import permissions

from potok_app.api.http_methods import *
from potok_app.api.profiles.permissions import DeleteProfileContentAccessPermission, \
    ProfilePreviewAccessPermission, IsProfileUsers, GetProfileContentAccessPermission
from potok_app.api.profiles.validators import is_valid_profile_id


class ProfileAttachmentAccessPermission(permissions.BasePermission):
    """
    Request permission

    - POST comment
        - only if avatars profile is users

    - GET comment
        - same as GET access to Profile Preview

    - DELETE comment
        - same as DELETE access to Profile
    """

    def has_permission(self, request, view):

        avatars_profile = is_valid_profile_id(view.kwargs['profile_id'])

        if request.method == GET:
            if view.action == 'current':
                return ProfilePreviewAccessPermission().has_object_permission(request, view, avatars_profile)
            return GetProfileContentAccessPermission().has_object_permission(request, view, avatars_profile)

        if request.method == POST:
            return IsProfileUsers().has_object_permission(request, view, avatars_profile)

        if request.method == DELETE:
            return DeleteProfileContentAccessPermission().has_object_permission(request, view, avatars_profile)

        return True
