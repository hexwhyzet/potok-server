import os

import django

from potok_users.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_app.models import Profile

admin = User.objects.filter(email="kabakov_ivan@mail.ru")

profiles = Profile.objects.exclude(user=admin)

ctr = 0

for profile in profiles.all():
    if profile.user is None:
        ctr += 1

print(ctr)

# print(User.objects.exclude(email="kabakov_ivan@mail.ru").count(), User.objects.count())

