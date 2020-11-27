from django.contrib import admin

from .models import Profile, Picture, Session, Like, Subscription, View

# Register your models here.

admin.site.register(Profile)
admin.site.register(Picture)
admin.site.register(Session)
admin.site.register(Like)
admin.site.register(Subscription)
admin.site.register(View)
