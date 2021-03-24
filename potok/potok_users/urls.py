from django.urls import path

from potok_users.views import RegistrationAPIView, LoginAPIView, AnonymousLoginAPIView, AnonymousRegistrationAPIView

urlpatterns = [
    path('app/registration',
         RegistrationAPIView.as_view(),
         name='user_registration'),

    path('app/login',
         LoginAPIView.as_view(),
         name='user_login'),

    path('app/anonymous_registration',
         AnonymousRegistrationAPIView.as_view(),
         name='anonymous_user_registration'),

    path('app/anonymous_login',
         AnonymousLoginAPIView.as_view(),
         name='anonymous_user_login'),
]
