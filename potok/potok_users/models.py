import random
from datetime import datetime, timedelta
from string import digits

import jwt
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from potok_app.models import Profile
from potok_app.services.profile.profile import generate_unique_screen_name


class UserManager(BaseUserManager):
    """
    Django требует, чтобы пользовательские `User`
    определяли свой собственный класс Manager.
    Унаследовав от BaseUserManager, мы получаем много кода,
    используемого Django для создания `User`.

    Все, что нам нужно сделать, это переопределить функцию
    `create_user`, которую мы будем использовать
    для создания объектов `User`.
    """

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Данный адрес электронной почты должен быть установлен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        profile = Profile(user=user, screen_name=generate_unique_screen_name())
        profile.save()

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и возвращает `User` с адресом электронной почты,
        именем пользователя и паролем.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_anonymous_user(self, **extra_fields):
        """
        Создает и возвращает анонимного `User` с кодом устройства
        """
        user = self.model(**extra_fields)
        user.save(using=self._db)

        profile = Profile(user=user)
        profile.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и возвращает пользователя с правами
        суперпользователя (администратора).
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def create_empty_user(self):
        user = self.model()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            'Designates whether this user verified his email.'
        ),
    )
    email = models.EmailField(
        _('email address'),
        blank=True,
        null=True,
        unique=True,
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    @property
    def is_authenticated(self):
        return self.email is not None

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # class Meta:
    #     constraints = [
    #         CheckConstraint(check=((Q(is_anonymous=True) & Q(email=None)) | (Q(is_anonymous=False) & ~Q(email=None))),
    #                         name='anonymous_user')
    #     ]

    def __str__(self):
        """
        Возвращает строковое представление этого `User`.
        Эта строка используется, когда в консоли выводится `User`.
        """
        if self.email:
            return self.email

        # if not self.is_verified and not self.is_staff and self.device_id:
        #     return self.device_id

        return "id" + str(self.id)

    @property
    def token(self):
        """
        Позволяет нам получить токен пользователя, вызвав `user.token` вместо
        `user.generate_jwt_token().

        Декоратор `@property` выше делает это возможным.
        `token` называется «динамическим свойством ».
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей,
        как обработка электронной почты.
        Обычно это имя и фамилия пользователя.
        Поскольку мы не храним настоящее имя пользователя,
        мы возвращаем его имя пользователя.
        """
        return self.email

    def get_short_name(self):
        """
        Этот метод требуется Django для таких вещей,
        как обработка электронной почты.
        Как правило, это будет имя пользователя.
        Поскольку мы не храним настоящее имя пользователя,
        мы возвращаем его имя пользователя.
        """
        return self.email

    def _generate_jwt_token(self):
        """
        Создает веб-токен JSON, в котором хранится идентификатор
        этого пользователя и срок его действия
        составляет 60 дней в будущем.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp()),
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    def send_verification_code(self):
        assert not self.is_anonymous
        assert not self.is_verified


class AccountVerificationCodeManager(models.Manager):
    CODE_LENGTH = 6

    def generate_code_string(self):
        return ''.join(random.choices(digits, k=self.CODE_LENGTH))

    def create_code(self, user):
        verification_code = self.model(user=user, email=user.email, code=self.generate_code_string())
        verification_code.save(using=self._db)
        return verification_code


class AccountVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    email = models.EmailField(
        _('email address'),
        blank=False,
        null=False,
    )
    date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    objects = AccountVerificationCodeManager()
    code = models.CharField(
        max_length=objects.CODE_LENGTH,
        blank=False,
        null=False,
    )
    attempts = models.SmallIntegerField(default=0)
