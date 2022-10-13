from django.urls import include, re_path, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from potok_app.api.avatars.views import AvatarViewSet
from potok_app.api.comments.views import CommentViewSet
from potok_app.api.importer import import_profiles, import_pictures
from potok_app.api.pictures.views import PictureViewSet
from potok_app.api.profile_attachments.views import ProfileAttachmentViewSet
from potok_app.api.profiles.views import ProfileViewSet

urlpatterns = []

router = SimpleRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
urlpatterns.append(re_path('', include(router.urls)))

nested_profile_router = routers.NestedSimpleRouter(router, r'profiles', lookup='profile')
router = SimpleRouter()
for iter_router in [router, nested_profile_router]:
    iter_router.register(r'pictures', PictureViewSet, basename='picture')
    iter_router.register(r'avatars', AvatarViewSet, basename='avatar')
    iter_router.register(r'attachments', ProfileAttachmentViewSet, basename='attachment')
urlpatterns.append(re_path('', include(router.urls)))
urlpatterns.append(re_path('', include(nested_profile_router.urls)))

nested_picture_router = routers.NestedSimpleRouter(router, r'pictures', lookup='picture')
router = SimpleRouter()
for iter_router in [router, nested_picture_router]:
    iter_router.register(r'comments', CommentViewSet, basename='comment')
urlpatterns.append(re_path('', include(router.urls)))
urlpatterns.append(re_path('', include(nested_picture_router.urls)))

urlpatterns.append(path('send_profiles', import_profiles))
urlpatterns.append(path('send_pictures', import_pictures))
