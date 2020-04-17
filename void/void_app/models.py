from django.db import models

# Create your models here.
from django.db import models


class Meme(models.Model):
    meme_picture = models.ImageField()
    dfd = models.CharField(max_length=100)
