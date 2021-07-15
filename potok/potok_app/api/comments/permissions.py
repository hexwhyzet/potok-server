from rest_framework import permissions
from rest_framework.permissions import IsAdminUser

from potok_app.api.global_permissions import DELETE
from potok_app.api.profiles.permissions import ProfileAccessPermission
from potok_app.services.profile import is_profile_users


class CommentAccessPermission(permissions.BasePermission):
    """
    Object-level permission to only allow

    - GET/HEAD/OPTIONS comment for
        - users that have access to the profile under whose picture the comment was left
        - user that owns profile that posted the comment

    - DELETE comment for (users must be eligible to GET comment)
        - user that owns profile under whose picture the comment was left
        - user that owns profile that posted the comment
        - admins

    - PUT/PATCH comment for (users must be eligible to DELETE comment)
        - user that own profile that posted the comment

    Assumes the comment model instance has an `picture` and `profile` attributes.
    """

    def has_object_permission(self, request, view, comment_obj):

        if is_profile_users(comment_obj.profile, request.user.profile):
            # This is the only case when PUT/PATCH request is available
            return True

        if ProfileAccessPermission().has_object_permission(request, view, comment_obj.profile):

            if request.method in permissions.SAFE_METHODS:
                return True

            if request.method == DELETE:
                return IsAdminUser().has_permission(request, view) \
                       or is_profile_users(comment_obj.picture.profile, request.user.profile)

        return False
