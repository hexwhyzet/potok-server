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
from django.urls import path, include

from . import views

urlpatterns = [
    path("share/<str:club_id>/<str:source_name>", views.share_picture),
    path("subscription_picture_app", views.subscription_picture_app),
    path("random_picture_app", views.random_picture_app),
    path("random_picture", views.view_random_picture),
    path("subscription_picture", views.view_subscription_picture),
    path("random_picture_mobile", views.view_random_picture_mobile),
    path("like_picture/<int:meme_id>", views.add_like_to_meme),
    path("send_posts", views.update_memes_db)
]
