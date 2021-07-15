from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

from potok_app.api.global_permissions import DELETE, PATCH, PUT
from potok_app.services.profile import is_profile_available, is_profile_users


class ProfileAccessPermission(permissions.BasePermission):
    """
    Object-level permission to only allow

    - GET/HEAD/OPTIONS profile for
        - users that have access to the profile

        If you've blocked the user or the user has blocked you returns False
        If profile is private and your subscription haven't been accepted by the user returns False
        Otherwise returns True

    - DELETE profile for (users must be eligible to GET comment)
        - user that owns the profile
        - admins

    - PUT/PATCH profile for (users must be eligible to DELETE comment)
        - user that owns the profile
    """

    def has_object_permission(self, request, view, profile_obj):

        if is_profile_available(request.user.profile, profile_obj):
            if request.method in permissions.SAFE_METHODS:
                return True

            if request.method == DELETE:
                return IsAdminUser().has_permission(request, view) \
                       or is_profile_users(request.user.profile, profile_obj)

            if request.method in [PUT, PATCH]:
                return is_profile_users(request.user.profile, profile_obj)

        return False
