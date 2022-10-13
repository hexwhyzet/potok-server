from django.contrib import admin
from django.utils.html import format_html

from potok_app.config import Secrets, Config
from potok_app.models import Profile, Picture, Session, Subscription, PictureView, Share, \
    Comment, PictureData, Avatar, ProfileSuggestion, ProfileAttachment, Like

admin.site.register(Avatar)
admin.site.register(PictureData)
admin.site.register(Session)
admin.site.register(Subscription)
admin.site.register(PictureView)
admin.site.register(Like)
admin.site.register(Share)
admin.site.register(Comment)
admin.site.register(ProfileSuggestion)

secrets = Secrets()
config = Config()


@admin.register(Profile)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "minor_id", "screen_name", "name")


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "date_timestamp", "profile_name", "profile_screen_name")
    ordering = ("-date",)

    @staticmethod
    def date_timestamp(picture: Picture):
        return int(picture.date.timestamp())

    @staticmethod
    def profile_name(picture: Picture):
        return picture.profile.name

    @staticmethod
    def profile_screen_name(picture: Picture):
        return picture.profile.screen_name

    # @staticmethod
    # def image_tag(picture: Picture):
    #     return format_html(
    #         f"<img src='{config['image_server_url']}/{config['image_server_bucket']}{high_resolution_url(picture)}' width='250' height='250'/>")


@admin.register(ProfileAttachment)
class ProfileAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "profile_name", "profile_screen_name", "tag", "url")

    @staticmethod
    def profile_name(profileAttachment: ProfileAttachment):
        return profileAttachment.profile.name

    @staticmethod
    def profile_screen_name(profileAttachment: ProfileAttachment):
        return profileAttachment.profile.screen_name
