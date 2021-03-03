import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_app.models import Profile

Profile.objects.filter(screen_name="username").delete()
