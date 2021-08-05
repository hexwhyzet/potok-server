from rest_framework import serializers

from potok_app.api.common_serializers import UnixEpochDateField
from potok_app.api.pictures.serializers import SizesMixin
from potok_app.models import Avatar
from potok_app.services.picture.avatar import create_avatar


class AvatarSerializer(serializers.ModelSerializer, SizesMixin):
    date = UnixEpochDateField(read_only=True)

    def create(self, validated_data):
        return create_avatar(**validated_data)

    class Meta:
        model = Avatar
        fields = ('id', 'date', 'sizes')
        read_only_fields = ('id', 'date', 'sizes')
