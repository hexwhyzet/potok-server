from rest_framework import serializers

from potok_app.api.common_serializers import UnixEpochDateField
from potok_app.models import Comment
from potok_app.services.comment.comment import create_comment


class CommentSerializer(serializers.ModelSerializer):
    date = UnixEpochDateField()

    def create(self, validated_data):
        return create_comment(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        return instance

    class Meta:
        model = Comment
        fields = ('id', 'text', 'date', 'likes_num',)
        read_only_fields = ('id', 'date', 'likes_num',)
