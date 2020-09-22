"""void URL Configuration

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
    # path("share/<str:club_id>/<str:source_name>", views.share_picture),
    path("app/subscription_picture/<str:session_token>", views.app_subscription_picture),
    path("app/feed_picture/<str:session_token>", views.app_feed_picture),
    # path("web/subscription_picture", views.view_subscription_picture),
    # path("web/random_picture", views.view_random_picture),
    # path("mweb/random_picture", views.view_random_picture_mobile),
    path("like_picture/<int:pic_id>", views.switch_like),
    path("subscribe/<int:club_id>", views.subscribe),
    path("send_posts", views.update_pics_db),
    path("send_clubs", views.update_profiles_db),
    path("create_session", views.create_session_request),
    # path("search/<str:search_string>", views.)
]
