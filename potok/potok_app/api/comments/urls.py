from django.urls import path

from potok_app.api.comments.views import CommentViewSet

comment_delete = CommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

comment_like = CommentViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
})

urlpatterns = [
    path('comments/'),
    path('comments/<int:comment_id>'),
    path('comments/<int:comment_id>/like'),
]
