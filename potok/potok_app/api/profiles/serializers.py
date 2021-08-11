from rest_framework import serializers

from potok_app.models import Profile
from potok_app.services.picture.avatar import get_current_avatar_or_gap_avatar


class ProfilePreviewSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, profile):
        from potok_app.api.avatars.serializers import AvatarSerializer
        return AvatarSerializer(get_current_avatar_or_gap_avatar(profile)).data

    class Meta:
        model = Profile
        fields = ('id', 'screen_name', 'avatar')
        read_only_fields = ('id', 'screen_name')


class ProfileSerializer(ProfilePreviewSerializer):
    class Meta:
        model = Profile
        fields = (
            'id',
            'views_num',
            'likes_num',
            'shares_num',
            'subs_num',
            'followers_num',
            'screen_name',
            'name',
            'avatar',
        )
        read_only_fields = ('id', 'views_num', 'likes_num', 'shares_num', 'subs_num', 'followers_num')


class ProfilePreviewMixin:
    profile_preview = serializers.SerializerMethodField()

    def get_profile_preview(self, picture):
        return ProfilePreviewSerializer(picture.profile).data
