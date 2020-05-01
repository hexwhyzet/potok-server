from django.contrib import admin

from .models import Profile, Club, Meme

# Register your models here.

admin.site.register(Meme)
admin.site.register(Profile)
admin.site.register(Club)
