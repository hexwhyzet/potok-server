from django.db import models

# Create your models here.
from django.db import models


class Meme(models.Model):
    meme_source_name = models.CharField(max_length=100, default='meme_source_name')
    meme_source_topic = models.CharField(max_length=100, default='meme_source_topic')
    meme_views = models.PositiveIntegerField(default=0)
    meme_likes = models.PositiveIntegerField(default=0)
    meme_picture = models.ImageField(upload_to='meme_images')

    def add_like(self):
        self.meme_likes += 1
