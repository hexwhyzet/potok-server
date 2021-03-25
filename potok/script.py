import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_app.models import User


