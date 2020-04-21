from django.db import models

# Create your models here.
from django.db import models


class MemeManager(models.Manager):
    def create_meme(self, meme_data, meme_picture):
        meme = self.create()
        meme.meme_source_name = str(meme_data['post_id'])
        meme.meme_source_topic = 57846937
        meme.meme_date = meme_data['date']
        meme.meme_pic_size = meme_data['photo']['size']
        meme.meme_picture = meme_picture
        return meme


class Meme(models.Model):
    meme_source_name = models.CharField(max_length=100)
    meme_source_topic = models.CharField(max_length=100)
    meme_views = models.PositiveIntegerField(default=0)
    meme_likes = models.PositiveIntegerField(default=0)
    meme_picture = models.ImageField(upload_to='meme_images')
    meme_pic_size = models.PositiveIntegerField(default=0)
    meme_date = models.PositiveIntegerField(default=0)

    objects = MemeManager()

    def add_like(self):
        self.meme_likes += 1
        self.save()
