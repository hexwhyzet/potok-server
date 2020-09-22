from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    minor_id = models.CharField(max_length=100, unique=True, blank=True)
    ip = models.CharField(max_length=100)
    name = models.CharField(max_length=100, default="", blank=True)
    screen_name = models.CharField(null=True, max_length=100, unique=True, blank=True)
    avatar_url = models.CharField(max_length=100, default="", blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    subs = models.ManyToManyField("self", symmetrical=False, related_name='followers', blank=True)


class Picture(models.Model):
    id = models.BigAutoField(primary_key=True)
    minor_id = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_url = models.CharField(max_length=100, blank=True)
    res = models.PositiveSmallIntegerField(default=0, blank=True)
    date = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='pics', blank=True, null=True)
    profiles_liked = models.ManyToManyField(Profile, related_name='pics_liked', blank=True)
    profiles_viewed = models.ManyToManyField(Profile, related_name='pics_viewed', blank=True)

    views_num = models.PositiveIntegerField(default=0)
    likes_num = models.PositiveIntegerField(default=0)
    shares_num = models.PositiveIntegerField(default=0)

    @classmethod
    def create(cls, profile, url=None, source_url=None, minor_id=None, res=None, date=None):
        picture = cls(
            profile=profile,
            minor_id=minor_id,
            url=url,
            source_url=source_url,
            res=res,
            date=date,
        )
        picture.save()
        return picture


class Session(models.Model):
    is_opened = models.BooleanField()
    token = models.SlugField(primary_key=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sub_pics = models.ManyToManyField(Picture, related_name='sessions_subscription', blank=True)
    feed_pics = models.ManyToManyField(Picture, related_name='sessions_random', blank=True)


class Link(models.Model):
    token = models.SlugField(primary_key=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links_sender', blank=False)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links_receiver', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content = GenericForeignKey('content_type', 'token')
