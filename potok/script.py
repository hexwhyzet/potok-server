import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_app.models import Profile

# profile = Profile.objects.get(screen_name="pictestempt").pics.order_by("-date")[4].id
# profile = Profile.objects.get(screen_name="dank_exe").pics.order_by("-date")[27].id
# profile = Profile.objects.get(screen_name="karkb").pics.order_by("-date")[16].id
# profile = Profile.objects.get(screen_name__startswith="teacheng").pics.order_by("-date")[15].id
profile = Profile.objects.get(screen_name__startswith="afroside").pics.order_by("-date")[29].id

print(profile)