from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

MINOR_ID_MAX_LENGTH = 100
SCREEN_NAME_MAX_LENGTH = 100
NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 100
COMMENT_MAX_LENGTH = 150


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    minor_id = models.CharField(max_length=MINOR_ID_MAX_LENGTH, null=True, default=None, unique=True, blank=True)
    screen_name = models.CharField(max_length=SCREEN_NAME_MAX_LENGTH, null=True, default=None, unique=True, blank=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, default=None, blank=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, null=True, default=None, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.SET_NULL, null=True)
    leaders = models.ManyToManyField('self', symmetrical=False, through='Subscription', related_name='followers',
                                     blank=True)
    blocked_profiles = models.ManyToManyField('self', symmetrical=False, through='ProfileBlock', blank=True)
    is_public = models.BooleanField(default=True)
    are_liked_pictures_public = models.BooleanField(default=False)

    views_num = models.PositiveIntegerField(default=0)
    likes_num = models.PositiveIntegerField(default=0)
    shares_num = models.PositiveIntegerField(default=0)
    subs_num = models.PositiveIntegerField(default=0)
    followers_num = models.PositiveIntegerField(default=0)

    def __str__(self):
        if self.name is not None:
            return f"{self.name} ({self.screen_name})"
        if self.screen_name is not None:
            return str(self.screen_name)
        if self.minor_id is not None:
            return str(self.minor_id)
        else:
            return f"unnamed user {self.id}"


class Avatar(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='avatars')
    source_url = models.CharField(max_length=1000, null=True, default=None, blank=True)
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)


class ProfileAttachment(models.Model):
    class Tag(models.Choices):
        VK = "vk"
        Reddit = "reddit"
        Custom = "custom"

    tag = models.CharField(choices=Tag.choices, max_length=100, default=Tag.Custom)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='attachments')
    url = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile', 'tag'], name='unique_tag')
        ]


class Picture(models.Model):
    id = models.BigAutoField(primary_key=True)
    minor_id = models.CharField(max_length=1000, null=True, default=None, blank=True)
    source_url = models.CharField(max_length=1000, null=True, default=None, blank=True)
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='pictures', blank=True, null=True)
    likes = GenericRelation('Like', related_query_name='picture', blank=True)
    profiles_viewed = models.ManyToManyField(Profile, through='PictureView', related_name='pictures_viewed', blank=True)
    link_url = models.CharField(max_length=100, default=None, null=True, blank=True)
    text = models.CharField(max_length=150, default=None, null=True, blank=True)

    recognized_text = models.CharField(max_length=1000, default=None, null=True, blank=True)

    views_num = models.PositiveIntegerField(default=0)
    likes_num = models.PositiveIntegerField(default=0)
    shares_num = models.PositiveIntegerField(default=0)
    comments_num = models.PositiveIntegerField(default=0)


class PictureData(models.Model):
    class PictureDataSizeType(models.TextChoices):
        TINY = 't', _('Tiny')
        SMALL = 's', _('Small')
        MEDIUM = 'm', _('Medium')
        BIG = 'b', _('Big')
        HUGE = 'h', _('Huge')

    path = models.CharField(max_length=200, null=False, blank=False)
    size_type = models.CharField(max_length=1, null=False, blank=False, choices=PictureDataSizeType.choices)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['object_id', 'content_type', 'size_type'], name='unique_size_type')
        ]


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='comments')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(validators=[MinLengthValidator(1)], max_length=COMMENT_MAX_LENGTH, blank=False, null=False)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    likes = GenericRelation('Like', related_query_name='picture', blank=True)
    likes_num = models.IntegerField(default=0)


class Like(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['object_id', 'content_type', 'profile'], name='unique_like')
        ]


class PictureView(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['picture', 'profile'], name='unique_view')
        ]


class Subscription(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sub_followers')
    leader = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sub_leaders')
    is_accepted = models.BooleanField(default=False, blank=False, null=False)
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'leader'], name='unique_subscription')
        ]


class ProfileBlock(models.Model):
    blocker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blockers')
    blocked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blocked')
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['blocker', 'blocked'], name='unique_block')
        ]


class PictureReport(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name="reports")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reports")
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['picture', 'profile'], name='unique_report')
        ]


class Session(models.Model):
    is_opened = models.BooleanField()
    token = models.SlugField(primary_key=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sub_pics = models.ManyToManyField(Picture, related_name='sessions_subscription', blank=True)
    feed_pics = models.ManyToManyField(Picture, related_name='sessions_random', blank=True)


class Share(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender_shares', blank=False)
    receiver = models.ManyToManyField(Profile, related_name='share_receiver', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField(null=True, blank=True)
    content = GenericForeignKey('content_type', 'object_id')


class ProfileSuggestion(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, null=True, blank=True)
