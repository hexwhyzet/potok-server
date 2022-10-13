from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from potok_users.api.users.views import AuthorizationViewSet

router = DefaultRouter()
router.register(r'users', AuthorizationViewSet, basename='user')

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
