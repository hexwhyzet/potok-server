"""potok URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views

urlpatterns = [
    path("app/my_profile", views.app_my_profile),
    path("app/subscription_pictures/<str:session_token>/<int:number>", views.app_subscription_pictures),
    path("app/feed_pictures/<str:session_token>/<int:number>", views.app_feed_pictures),
    path("app/profile_pictures/<int:profile_id>/<int:number>/<int:offset>", views.profile_pictures),
    path("app/like_picture/<int:pic_id>", views.app_switch_like),
    path("app/subscribe/<int:sub_profile_id>", views.app_switch_subscription),
    path("app/create_session", views.create_session_request),
    path("app/upload_picture", views.upload_picture),
    path("app/mark_as_seen/<int:pic_id>", views.mark_as_seen),
    path("app/last_actions/<int:number>/<int:offset>", views.last_actions),
    path("app/share_profile/<str:profile_id>", views.generate_profile_share_link),
    path("app/share_picture/<str:pic_id>", views.generate_picture_share_link),
    path("share/<str:share_token>", views.content_by_link),
    # path("search/<str:search_string>", views.)

    path("auth/device_id", views.log_in_via_device_id),

    path("send_clubs", views.update_profiles_db),
    path("send_posts", views.update_pics_db),

    # path("web/subscription_picture", views.view_subscription_picture),
    # path("web/random_picture", views.view_random_picture),
    # path("mweb/random_picture", views.view_random_picture_mobile),
]
