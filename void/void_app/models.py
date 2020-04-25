from django.db import models


# Create your models here.


class MemeManager(models.Manager):
    def create_meme(self, meme_data, meme_picture):
        meme = self.create()
        meme.source_name = "vk"
        meme.source_id = str(meme_data['post_id'])
        meme.picture = meme_picture
        meme.pic_size = meme_data['photo']['size']
        meme.date = meme_data['date']
        return meme


class Meme(models.Model):
    source_name = models.CharField(max_length=100)
    source_id = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='saved_pics', default="")
    pic_size = models.PositiveIntegerField(default=0)
    date = models.PositiveIntegerField(default=0)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    objects = MemeManager()

    def add_like(self):
        self.likes += 1
        self.save()
