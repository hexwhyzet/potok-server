from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

from potok_app.api.http_methods import DELETE, PATCH, GET
from potok_app.services.profile.profile import is_profile_content_available, is_profile_users


class ProfilePreviewAccessPermission(permissions.BasePermission):
    """
    Permission to brief information about profile

    - GET allowed for everyone
    """

    def has_object_permission(self, request, view, profile_obj):
        if request.method == GET:
            return True

        return False


class ProfileContentAccessPermission(permissions.BasePermission):
    """
    Permission to content of profile

    - GET profile for
        - users that have access to the profile

        If you've blocked the user or the user has blocked you returns False
        If profile is private and your subscriptions haven't been accepted by the user returns False
        Otherwise returns True

    - DELETE profile for
        - user that owns the profile
        - admins

    - PATCH profile for
        - user that owns the profile
    """

    def has_object_permission(self, request, view, profile_obj):

        if request.method == GET:
            return GetProfileContentAccessPermission().has_object_permission(request, view, profile_obj)

        if request.method == DELETE:
            return DeleteProfileContentAccessPermission().has_object_permission(request, view, profile_obj)

        if request.method == PATCH:
            return PatchProfileContentAccessPermission().has_object_permission(request, view, profile_obj)

        return False


class GetProfileContentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, profile_obj):
        return is_profile_content_available(request.user.profile, profile_obj)


class DeleteProfileContentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, profile_obj):
        return IsAdminUser().has_permission(request, view) \
               or IsProfileUsers().has_object_permission(request, view, profile_obj)


class PatchProfileContentAccessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, profile_obj):
        return IsProfileUsers().has_object_permission(request, view, profile_obj)


class IsProfileUsers(permissions.BasePermission):

    def has_object_permission(self, request, view, profile_obj):
        return is_profile_users(request.user.profile, profile_obj)
