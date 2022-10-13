import datetime
import time

from rest_framework import serializers


class UnixEpochDateField(serializers.DateTimeField):
    def to_representation(self, value):
        """ Return epoch time for a datetime object or ``None``"""
        try:
            return int(time.mktime(value.timetuple()))
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        return datetime.datetime.fromtimestamp(int(value))


class UserProfileContext(serializers.Serializer):
    def get_user_profile(self):
        return self.context['request'].user.profile
