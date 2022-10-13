from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from potok_app.api.http_methods import GET, DELETE, PUT
from potok_app.api.paginations import StandardResultsSetPagination
from potok_app.api.profiles.permissions import ProfilePreviewAccessPermission, GetProfileContentAccessPermission
from potok_app.api.profiles.serializers import ProfileSerializer, ProfilePreviewSerializer
from potok_app.services.profile.profile import followers, leaders, available_profiles
from potok_app.services.profile.profile_block import does_block_exist, delete_block, create_block
from potok_app.services.profile.profile_subscription import safe_delete_subscription, \
    safe_create_subscription


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = []
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = available_profiles()
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=[GET], permission_classes=[ProfilePreviewAccessPermission],
            serializer_class=ProfilePreviewSerializer)
    def preview(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(detail=True, methods=[PUT, DELETE],
            permission_classes=[IsAuthenticated, GetProfileContentAccessPermission])
    def subscription(self, request, *args, **kwargs):
        leader = self.get_object()
        follower = self.request.user.profile

        if request.method == DELETE:
            safe_delete_subscription(follower, leader)
        if request.method == PUT:
            safe_create_subscription(follower, leader)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=[PUT, DELETE],
            permission_classes=[IsAuthenticated, ProfilePreviewAccessPermission])
    def block(self, request, *args, **kwargs):
        blocked = self.get_object()
        blocker = self.request.user.profile

        if does_block_exist(blocker, blocked):
            if request.method == DELETE:
                delete_block(blocker, blocked)
        else:
            if request.method == PUT:
                create_block(blocker, blocked)
        return Response(status=blocker.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=[GET])
    def followers(self, request, *args, **kwargs):
        profiles = followers(self.get_object())

        page = self.paginate_queryset(profiles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=[GET])
    def leaders(self, request, *args, **kwargs):
        profiles = leaders(self.get_object())

        page = self.paginate_queryset(profiles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

# class ProfileSubscriptionViewSetBase(GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
#     serializer_class = ProfilePreviewSerializer
#     permission_classes = []
#     lookup_field = 'id'
#     lookup_url_kwarg = 'id'
#     pagination_class = StandardResultsSetPagination
#
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return ProfileSerializer
#         return ProfilePreviewSerializer
#
#
# class FollowerViewSet(ProfileSubscriptionViewSetBase):
#     def get_queryset(self):
#         profile = is_valid_profile_id(self.kwargs.get('profile_id'))
#         return profile.followers.all()
#
#
# class LeaderViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
#     def get_queryset(self):
#         profile = is_valid_profile_id(self.kwargs.get('profile_id'))
#         return profile.leaders.all()
