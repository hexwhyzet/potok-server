from rest_framework import permissions
from rest_framework.permissions import BasePermission

from potok_app.api.http_methods import *
from potok_users.models import User


class AuthorizationAccessPermission(permissions.BasePermission):
    """
    - POST comment for
        - for everyone
    """

    def has_permission(self, request, view):
        if request.method == POST:
            return True

        return False


class TokenAuthorizationRequired(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user == User)
