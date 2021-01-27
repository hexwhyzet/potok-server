from django.contrib import admin

from potok_app.models import Profile, Picture, Session, Like, Subscription, View, CustomAnonymousUser, CustomUser, Link, \
    Comment, CommentLike, PictureData, Avatar, AvatarData, ProfileSuggestion

# Register your models here.

admin.site.register(Profile)
admin.site.register(Picture)
admin.site.register(PictureData)
admin.site.register(Session)
admin.site.register(Like)
admin.site.register(Subscription)
admin.site.register(View)
admin.site.register(CustomAnonymousUser)
admin.site.register(CustomUser)
admin.site.register(Link)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Avatar)
admin.site.register(AvatarData)
admin.site.register(ProfileSuggestion)
