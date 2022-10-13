from rest_framework import serializers

from potok_app.api.common_serializers import UserProfileContext
from potok_app.api.profile_attachments.serializers import ProfileAttachmentSerializer
from potok_app.models import Profile
from potok_app.services.picture.avatar import get_current_avatar_or_gap_avatar
from potok_app.services.profile.profile import is_profile_content_available, is_profile_users, get_block_status, \
    get_subscription_status, is_liked_pictures_page_available


class ProfilePreviewSerializer(serializers.ModelSerializer, UserProfileContext):
    is_yours = serializers.SerializerMethodField()

    def get_is_yours(self, profile):
        return is_profile_users(self.get_user_profile(), profile)

    is_available = serializers.SerializerMethodField()

    def get_is_available(self, profile):
        return is_profile_content_available(self.get_user_profile(), profile)

    is_liked_pictures_page_available = serializers.SerializerMethodField()

    def get_is_liked_pictures_page_available(self, profile):
        return is_liked_pictures_page_available(self.get_user_profile(), profile)

    is_private = serializers.SerializerMethodField()

    def get_is_private(self, profile):
        return profile.is_private

    block_status = serializers.SerializerMethodField()

    def get_block_status(self, profile):
        return get_block_status(self.get_user_profile(), profile)

    subscription_status = serializers.SerializerMethodField()

    def get_subscription_status(self, profile):
        return get_subscription_status(self.get_user_profile(), profile)

    avatar = serializers.SerializerMethodField()

    def get_avatar(self, profile):
        from potok_app.api.avatars.serializers import AvatarSerializer
        return AvatarSerializer(get_current_avatar_or_gap_avatar(profile)).data

    class Meta:
        model = Profile
        fields = (
            'id',
            'screen_name',
            'is_yours',
            'is_available',
            'is_private',
            'is_liked_pictures_page_available',
            'block_status',
            'subscription_status',
            'avatar',
        )
        read_only_fields = ('id', 'screen_name')


class ProfileSerializer(ProfilePreviewSerializer):
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, profile):
        return ProfileAttachmentSerializer(profile.attachments, many=True).data

    class Meta:
        model = Profile
        fields = (
            'id',
            'is_yours',
            'is_available',
            'is_private',
            'is_liked_pictures_page_available',
            'block_status',
            'subscription_status',
            'views_num',
            'likes_num',
            'shares_num',
            'leaders_num',
            'followers_num',
            'screen_name',
            'name',
            'description',
            'avatar',
            'attachments',
        )
        read_only_fields = ('id', 'views_num', 'likes_num', 'shares_num', 'subs_num', 'followers_num')
