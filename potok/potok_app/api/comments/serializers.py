from rest_framework import serializers

from potok_app.models import Comment, COMMENT_MAX_LENGTH


class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(max_length=COMMENT_MAX_LENGTH)
    date = serializers.DateTimeField(read_only=True)
    likes_num = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        return instance

    class Meta:
        model = Comment
        fields = ["id", "text", "date", "likes_num"]
