from django.db import models

# Create your models here.
from django.db import models


class Meme(models.Model):
    meme_picture = models.ImageField(upload_to='meme_images')
