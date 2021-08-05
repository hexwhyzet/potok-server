from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from potok_app.api.http_methods import POST, GET
from potok_users.api.users.serializers import AuthorizationSerializer
from potok_users.services.users import create_anonymous_user
from potok_users.services.verification_codes import create_account_verification_code, \
    does_account_verification_code_exist


class AuthorizationViewSet(GenericViewSet):
    permission_classes = []
    serializer_class = AuthorizationSerializer

    def get_object(self):
        email = self.request.data.get('email', None)
        password = self.request.data.get('password', None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise ValidationError('A user with this email and password was not found.')
        return user

    @action(detail=False, methods=[POST])
    def register(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=[POST])
    def login(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=[POST])
    def anonymous(self, request, *args, **kwargs):
        user = create_anonymous_user()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=[GET, POST])
    def verify(self, request, *args, **kwargs):
        user = request.user
        if request.method == GET:
            create_account_verification_code(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == POST:
            code = self.request.data.get('code', None)
            if does_account_verification_code_exist(user, code):
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
