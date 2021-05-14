from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

MINOR_ID_MAX_LENGTH = 100
SCREEN_NAME_MAX_LENGTH = 100
NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 100


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    minor_id = models.CharField(max_length=MINOR_ID_MAX_LENGTH, null=True, default=None, unique=True, blank=True)
    screen_name = models.CharField(max_length=SCREEN_NAME_MAX_LENGTH, null=True, default=None, unique=True, blank=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, default=None, blank=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, null=True, default=None, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.SET_NULL, null=True)
    subs = models.ManyToManyField('self', symmetrical=False, through='Subscription', related_name='followers',
                                  blank=True)
    blocked_profiles = models.ManyToManyField('self', symmetrical=False, through='ProfileBlock', blank=True)
    is_public = models.BooleanField(default=True)
    are_liked_pictures_public = models.BooleanField(default=False)

    views_num = models.PositiveIntegerField(default=0)
    likes_num = models.PositiveIntegerField(default=0)
    shares_num = models.PositiveIntegerField(default=0)
    subs_num = models.PositiveIntegerField(default=0)
    followers_num = models.PositiveIntegerField(default=0)


class Avatar(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='avatars')
    source_url = models.CharField(max_length=1000, null=True, default=None, blank=True)
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)


class AvatarData(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='avatar_data')
    url = models.CharField(max_length=100, default=None, null=True, blank=True)
    res = models.PositiveSmallIntegerField()


class ProfileAttachment(models.Model):

    class Tag(models.Choices):
        VK = "vk"
        Custom = "custom"

    tag = models.CharField(choices=Tag.choices, max_length=100, default=Tag.Custom)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='attachments')
    url = models.CharField(max_length=100)


class Picture(models.Model):
    id = models.BigAutoField(primary_key=True)
    minor_id = models.CharField(max_length=1000, null=True, default=None, blank=True)
    source_url = models.CharField(max_length=1000, null=True, default=None, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='pics', blank=True, null=True)
    profiles_liked = models.ManyToManyField(Profile, through='Like', related_name='pics_liked', blank=True)
    profiles_viewed = models.ManyToManyField(Profile, through='View', related_name='pics_viewed', blank=True)
    link_url = models.CharField(max_length=100, default=None, null=True, blank=True)
    text = models.CharField(max_length=150, default=None, null=True, blank=True)

    views_num = models.PositiveIntegerField(default=0)
    likes_num = models.PositiveIntegerField(default=0)
    shares_num = models.PositiveIntegerField(default=0)

    @classmethod
    def create(cls, profile, link_url=None, source_url=None, minor_id=None, date=None):
        picture = cls(
            profile=profile,
            source_url=source_url,
            minor_id=minor_id,
            link_url=link_url,
            date=date,
        )
        picture.save()
        return picture


class PictureData(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='picture_data')
    url = models.CharField(max_length=100, default=None, null=True, blank=True)
    res = models.PositiveSmallIntegerField()


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='comments')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=150, blank=False, null=False)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    profiles_liked = models.ManyToManyField(Profile, through='CommentLike', related_name='comments_liked', blank=True)
    likes_num = models.IntegerField(default=0)


class Like(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class View(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class Subscription(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sub_followers')
    source = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sub_sources')
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'source')


class ProfileBlock(models.Model):
    blocker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blockers')
    blocked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blocked')
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class PictureReport(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports")
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name="reports")
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class Session(models.Model):
    is_opened = models.BooleanField()
    token = models.SlugField(primary_key=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sub_pics = models.ManyToManyField(Picture, related_name='sessions_subscription', blank=True)
    feed_pics = models.ManyToManyField(Picture, related_name='sessions_random', blank=True)


class Link(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links_sender', blank=False)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links_receiver', blank=True,
                                 null=True)
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField(null=True, blank=True)
    content = GenericForeignKey('content_type', 'object_id')


class ProfileSuggestion(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, null=True, blank=True)
