from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView


class CustomListAPIView(ListAPIView):
    COUNT_LIMIT = 100
    COUNT_DEFAULT = 10
    OFFSET_DEFAULT = 0

    def extract_count(self):
        count = self.request.query_params.get('count', default=self.COUNT_DEFAULT)
        if count > self.COUNT_LIMIT:
            raise ValidationError(f"`count` parameter is bigger than the limit (limit is {self.COUNT_LIMIT}")
        return count

    def extract_offset(self):
        offset = self.request.query_params.get('offset', default=self.OFFSET_DEFAULT)
        return offset
