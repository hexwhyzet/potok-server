from rest_framework import permissions

from potok_app.api.http_methods import *


class AuthorizationAccessPermission(permissions.BasePermission):
    """
    - POST comment for
        - for everyone
    """

    def has_permission(self, request, view):
        if request.method == POST:
            return True

        return False
