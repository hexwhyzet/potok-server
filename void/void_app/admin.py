from django.contrib import admin

from .models import Profile, Picture, Session

# Register your models here.

admin.site.register(Profile)
admin.site.register(Picture)
admin.site.register(Session)
