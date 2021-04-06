import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_users.models import User

# User.objects.create_user(email="appleverification@potok.app", password="TbbCYZPJJC")

User.objects.create_user(email="googleplayverification@potok.app", password="vBgubxNRdZ")

# print(User.objects.exclude(email="kabakov_ivan@mail.ru").count(), User.objects.count())
