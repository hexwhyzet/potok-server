from django.db import models
from django.conf import settings
from .functions import id_gen


class MemeManager(models.Manager):
    def create_meme(self, meme_data, meme_picture, club):
        meme = self.create()
        # meme.id = id_gen(length=6)
        meme.source_name = "vk"
        meme.source_id = str(meme_data['post_id'])
        meme.picture = meme_picture
        meme.size = meme_data['photo']['size']
        meme.date = meme_data['date']
        meme.club = club
        return meme


class Club(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True)


class Meme(models.Model):
    # id = models.CharField(max_length=6, primary_key=True, default=id_gen)
    source_name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='saved_pics', default="")
    size = models.PositiveIntegerField(default=0)
    date = models.PositiveIntegerField(default=0)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    objects = MemeManager()

    def add_like(self):
        self.likes += 1
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    ip = models.CharField(max_length=100)
    seen_memes = models.ManyToManyField(Meme, related_name='profile', blank=True)
    subscriptions = models.ManyToManyField(Club, related_name='profile', blank=True)

    def add_ip(self, ip):
        self.ip = ip
