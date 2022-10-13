from rest_framework.viewsets import ModelViewSet

from potok_app.api.mixins import FiltersMixin
from potok_app.api.paginations import SmallResultsSetPagination
from potok_app.api.profile_attachments.serializers import ProfileAttachmentSerializer
from potok_app.services.profile.profile_attachment import available_attachments


class ProfileAttachmentViewSet(ModelViewSet, FiltersMixin):
    serializer_class = ProfileAttachmentSerializer
    permission_classes = []
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = available_attachments()

    def perform_create(self, serializer):
        profile = self.get_kwargs_profile()
        serializer.save(profile=profile)
