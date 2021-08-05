from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from potok_app.api.avatars.views import AvatarViewSet
from potok_app.api.comments.views import CommentViewSet
from potok_app.api.pictures.views import PictureViewSet
from potok_app.api.profiles.views import ProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')

profile_router = routers.NestedSimpleRouter(router, r'profiles', lookup='profile')
profile_router.register(r'pictures', PictureViewSet, basename='picture')
profile_router.register(r'avatars', AvatarViewSet, basename='avatar')

picture_router = routers.NestedSimpleRouter(profile_router, r'pictures', lookup='picture')
picture_router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(profile_router.urls)),
    url(r'^', include(picture_router.urls)),
]
