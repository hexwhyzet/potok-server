from rest_framework import serializers

from potok_app.models import ProfileAttachment


class ProfileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileAttachment
        fields = ('id', 'tag', 'url',)
        read_only_fields = ('id',)
