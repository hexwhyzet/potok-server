from rest_framework import serializers

from potok_app.api.common_serializers import UnixEpochDateField, UserProfileContext
from potok_app.api.profiles.serializers import ProfilePreviewSerializer
from potok_app.models import PictureData, Picture
from potok_app.object_storage_api import get_bucket_url
from potok_app.services.like.like import does_like_exist
from potok_app.services.picture.picture import create_picture
from potok_app.services.picture.picture_data import get_picture_data_by_content_object


class SizesMixin(serializers.Serializer):
    sizes = serializers.SerializerMethodField()

    def get_sizes(self, picture):
        result = PictureDataSerializer(get_picture_data_by_content_object(picture), many=True).data
        return list(sorted(result, key=lambda x: PictureData.PictureDataSizeType.values.index(x['size_type'])))


class PictureSerializer(serializers.ModelSerializer, SizesMixin, UserProfileContext):
    profile_preview = serializers.SerializerMethodField()

    def get_profile_preview(self, picture):
        return ProfilePreviewSerializer(picture.profile, context=self.context).data

    date = UnixEpochDateField(read_only=True)

    def get_is_liked(self, picture):
        return does_like_exist(picture, self.get_user_profile())

    is_liked = serializers.SerializerMethodField()

    def create(self, validated_data):
        return create_picture(**validated_data)

    class Meta:
        model = Picture
        fields = (
            'id',
            'date',
            'text',
            'link_url',
            'views_num',
            'likes_num',
            'is_liked',
            'shares_num',
            'comments_num',
            'profile_preview',
            'sizes',
        )
        read_only_fields = (
            'id',
            'date',
            'views_num',
            'likes_num',
            'is_liked',
            'shares_num',
            'comments_num',
            'profile_preview',
            'sizes',
        )


class PictureDataSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, picture_data):
        return get_bucket_url() + picture_data.path

    class Meta:
        model = PictureData
        fields = ('url', 'size_type', 'width', 'height',)
        read_only_fields = ('url', 'size_type', 'width', 'height',)
