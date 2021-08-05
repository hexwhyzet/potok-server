from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from potok_users.api.users.views import AuthorizationViewSet

router = DefaultRouter()
router.register(r'users', AuthorizationViewSet, basename='user')

urlpatterns = [
    url(r'^', include(router.urls)),
]
