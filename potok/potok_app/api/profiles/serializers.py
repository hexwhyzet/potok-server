from rest_framework import serializers

from potok_app.models import Profile


class ProfilePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'screen_name')
        read_only_fields = ('id', 'screen_name')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'views_num', 'likes_num', 'shares_num', 'subs_num', 'followers_num', 'screen_name', 'name')
        read_only_fields = ('id', 'views_num', 'likes_num', 'shares_num', 'subs_num', 'followers_num')
