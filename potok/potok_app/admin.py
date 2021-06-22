from django.contrib import admin
from django.utils.html import format_html

from potok_app.config import Secrets, Config
from potok_app.models import Profile, Picture, Session, Like, Subscription, View, Link, \
    Comment, CommentLike, PictureData, Avatar, AvatarData, ProfileSuggestion, ProfileAttachment
from potok_app.services.picture import high_resolution_url

admin.site.register(Profile)

secrets = Secrets()
config = Config()


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "profile_name", "profile_screen_name", "image_tag")

    @staticmethod
    def profile_name(picture: Picture):
        return picture.profile.name

    @staticmethod
    def profile_screen_name(picture: Picture):
        return picture.profile.screen_name

    @staticmethod
    def image_tag(picture: Picture):
        return format_html(
            f"<img src='{config['image_server_url']}/{config['image_server_bucket']}{high_resolution_url(picture)}' width='250' height='250'/>")


admin.site.register(PictureData)
admin.site.register(Session)
admin.site.register(Like)
admin.site.register(Subscription)
admin.site.register(View)
admin.site.register(Link)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Avatar)
admin.site.register(AvatarData)
admin.site.register(ProfileSuggestion)


@admin.register(ProfileAttachment)
class ProfileAttachmentAdmin(admin.ModelAdmin):
    list_display = ("profile_name", "profile_screen_name", "tag", "url")

    @staticmethod
    def profile_name(profileAttachment: ProfileAttachment):
        return profileAttachment.profile.name

    @staticmethod
    def profile_screen_name(profileAttachment: ProfileAttachment):
        return profileAttachment.profile.screen_name
