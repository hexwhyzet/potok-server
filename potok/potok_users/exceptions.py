from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class InvalidToken(APIException):
    staticmethod = 403
    default_detail = 'Token is invalid.'
    default_code = 'service_unavailable'


class InvalidEmail(APIException):
    status_code = 503
    default_detail = 'Email is not available.'
    default_code = 'service_unavailable'


class EmailIsAlreadyTaken(APIException):
    status_code = 503
    default_detail = 'Email is already taken.'
    default_code = 'service_unavailable'


class PasswordIsTooShort(APIException):
    status_code = 503
    default_detail = 'Password is too short.'
    default_code = 'service_unavailable'


class PasswordIsTooLong(APIException):
    status_code = 503
    default_detail = 'Password is too long.'
    default_code = 'service_unavailable'


class PasswordContainsInvalidCharacters(APIException):
    status_code = 503
    default_detail = 'Password contains invalid characters.'
    default_code = 'service_unavailable'


class NoUserFound(APIException):
    status_code = 503
    default_detail = 'A user with this email and password was not found.'
    default_code = 'service_unavailable'


class UserIsInactive(APIException):
    status_code = 503
    default_detail = 'This user has been deactivated.'
    default_code = 'service_unavailable'
