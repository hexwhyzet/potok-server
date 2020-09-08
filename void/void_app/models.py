from django.db import models
from django.conf import settings
from .functions import id_gen


class MemeManager(models.Manager):
    def create_meme(self, meme_data, pic_path, club):
        meme = self.create()
        meme.source_name = "vk"
        meme.source_id = str(meme_data['post_id'])
        meme.picture_url = pic_path
        meme.size = meme_data['photo']['size']
        meme.date = meme_data['date']
        meme.club = club
        return meme


class Club(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)
    profile_picture_url = models.CharField(max_length=100, default="")
    name = models.CharField(max_length=100, default="")
    screen_name = models.CharField(max_length=100, default="")


class Meme(models.Model):
    source_name = models.CharField(max_length=100)
    picture_url = models.CharField(max_length=100, default="")
    size = models.PositiveIntegerField(default=0)
    date = models.PositiveIntegerField(default=0)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    objects = MemeManager()

    def add_like(self):
        self.likes += 1
        self.save()

    def remove_like(self):
        self.likes -= 1
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    ip = models.CharField(max_length=100)
    seen_memes = models.ManyToManyField(Meme, related_name='seen_profile', blank=True)
    liked_memes = models.ManyToManyField(Meme, related_name='liked_profile', blank=True)
    subscriptions = models.ManyToManyField(Club, related_name='sub_profile', blank=True)

    def add_ip(self, ip):
        self.ip = ip


class Session(models.Model):
    is_opened = models.BooleanField()
    token = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    subscription_memes = models.ManyToManyField(Meme, related_name='sessions_subscription', blank=True)
    random_memes = models.ManyToManyField(Meme, related_name='sessions_random', blank=True)

