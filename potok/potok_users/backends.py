from string import ascii_lowercase, ascii_uppercase, digits

import jwt
from MailChecker import MailChecker
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import authentication, exceptions, serializers
from rest_framework.validators import UniqueValidator

from potok_users.exceptions import InvalidEmail, PasswordIsTooShort, PasswordIsTooLong, PasswordContainsInvalidCharacters, \
    NoUserFound, UserIsInactive
from .config import Config
from .models import User, VerificationCode

config = Config()

MAX_PASSWORD_LENGTH = 128
MIN_PASSWORD_LENGTH = 8
PASSWORD_CHARACTERS = ascii_lowercase + ascii_uppercase + digits + "~`!@#$%^&*()_-+={[}]|\:;\"'<,>.?/"


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The Token string should not contain spaces.
            # Do not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a new user.
    Email, username, and password are required.
    Returns a JSON web token.
    """
    code = serializers.CharField(
        max_length=100,
        write_only=True,
    )
    # The password must be validated and should not be read by the client
    password = serializers.CharField(
        max_length=MAX_PASSWORD_LENGTH,
        min_length=MIN_PASSWORD_LENGTH,
        write_only=True,
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token', 'code',)

    def validate(self, data):
        email = data.get('email', None)
        code = data.get('code', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to register.'
            )

        if code is None:
            raise serializers.ValidationError(
                'A code is required to register.'
            )

        if not VerificationCode.objects.filter(email=email, code=code).exists():
            raise exceptions.AuthenticationFailed('Invalid verification code.')

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ValidateCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password',)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if not MailChecker.is_valid(email):
            raise InvalidEmail()

        for letter in password:
            if letter not in PASSWORD_CHARACTERS:
                raise PasswordContainsInvalidCharacters()

        if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
            if len(password) < 8:
                raise PasswordIsTooShort()
            else:
                raise PasswordIsTooLong()

        return data


class AnonymousRegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a new anonymous user.
    Device id is required.
    Returns a JSON web token.
    """

    device_id = serializers.CharField(max_length=200, validators=[
        UniqueValidator(queryset=User.objects.all(), message='User with this device id is already exist')])

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('device_id', 'token',)

    def create(self, validated_data):
        return User.objects.create_anonymous_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=MAX_PASSWORD_LENGTH, write_only=True)

    # Ignore these fields if they are included in the request.
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(email=email, password=password)

        if user is None:
            raise NoUserFound()

        if not user.is_active:
            raise UserIsInactive()

        return {
            'token': user.token,
        }


class AnonymousLoginSerializer(serializers.Serializer):
    """
    Authenticates anonymous account.
    Device id is required.
    Returns a JSON web token.
    """
    device_id = serializers.CharField(max_length=200, write_only=True)

    # Ignore these fields if they are included in the request.
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        device_id = data.get('device_id', None)

        if device_id is None:
            raise serializers.ValidationError(
                'A device id is required'
            )

        if User.objects.filter(device_id=device_id).filter(is_verified=True).exists():
            raise serializers.ValidationError(
                'This device id is already registered'
            )

        if not User.objects.filter(device_id=device_id).exists():
            user = User.objects.create_anonymous_user(device_id=device_id)
        else:
            user = User.objects.filter(device_id=device_id).filter(is_verified=False).first()

        # if user is None:
        #     raise serializers.ValidationError(
        #         'A user with this  device id is not found'
        #     )

        return {
            'token': user.token,
        }


class InitiateVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = VerificationCode
        fields = ('email', 'code',)

    def create(self, validated_data):
        """
        Validates user data.
        """
        email = validated_data.get('email', None)

        if email is None:
            raise serializers.ValidationError(
                'Missing email data'
            )

        if User.objects.filter(email=email, is_verified=True).exists():
            raise serializers.ValidationError(
                'User with this email is already registered'
            )

        VerificationCode.objects.filter(email=email).delete()

        code = VerificationCode.objects.create_code(email=email)

        send_mail(
            "Email verification",
            f"""
  Hello! 
  Thank you for your registration in Potok. Please use the code below to verificate your email:

  {code.code}

  Thanks!
 
  Potok team
            """,
            config["email_host_user"],
            [email],
        )
        return code
