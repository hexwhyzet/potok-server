from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    minor_id = models.CharField(null=True, default=None, max_length=100, unique=True, blank=True)
    ip = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, null=True, default=None, blank=True)
    screen_name = models.CharField(max_length=100, null=True, default=None, unique=True, blank=True)
    avatar_url = models.CharField(max_length=100, null=True, default=None, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    subs = models.ManyToManyField('self', symmetrical=False, through='Subscription', related_name='followers',
                                  blank=True)


class Picture(models.Model):
    id = models.BigAutoField(primary_key=True)
    minor_id = models.CharField(null=True, default=None, max_length=100, blank=True)
    url = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_url = models.CharField(null=True, default=None, max_length=100, blank=True)
    res = models.PositiveSmallIntegerField(null=True, default=0, blank=True)
    date = models.DateTimeField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='pics', blank=True, null=True)
    profiles_liked = models.ManyToManyField(Profile, through='Like', related_name='pics_liked', blank=True)
    profiles_viewed = models.ManyToManyField(Profile, through='View', related_name='pics_viewed', blank=True)

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
