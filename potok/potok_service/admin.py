from django.contrib import admin

from .models import Profile, Picture, Session, Like, Subscription, View, CustomAnonymousUser, CustomUser, Link

# Register your models here.

admin.site.register(Profile)
admin.site.register(Picture)
admin.site.register(Session)
admin.site.register(Like)
admin.site.register(Subscription)
admin.site.register(View)
admin.site.register(CustomAnonymousUser)
admin.site.register(CustomUser)
admin.site.register(Link)
