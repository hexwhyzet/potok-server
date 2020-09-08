from django.contrib import admin

from .models import Profile, Club, Meme, Session

# Register your models here.

admin.site.register(Meme)
admin.site.register(Profile)
admin.site.register(Club)
admin.site.register(Session)
