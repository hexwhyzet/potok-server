from django.urls import path

from potok_users.views import RegistrationAPIView, LoginAPIView, AnonymousLoginAPIView, AnonymousRegistrationAPIView, \
    is_logged, InitiateVerification, ValidateCredentialsAPIView

urlpatterns = [
    path('app/registration',
         RegistrationAPIView.as_view(),
         name='user_registration'),

    path('app/validate_credentials', ValidateCredentialsAPIView.as_view(), name='validate_credentials'),

    path('app/login',
         LoginAPIView.as_view(),
         name='user_login'),

    path('app/anonymous_registration',
         AnonymousRegistrationAPIView.as_view(),
         name='anonymous_user_registration'),

    path('app/anonymous_login',
         AnonymousLoginAPIView.as_view(),
         name='anonymous_user_login'),

    path('app/is_logged', is_logged),

    path('app/initiate_verification', InitiateVerification.as_view(), name='initiate_verification'),
]
