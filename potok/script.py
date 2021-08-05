import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'potok.settings')
django.setup()

from potok_app.models import Profile

from potok_recommender.models import Ticket

from potok_users.models import User

# profile = Profile.objects.get(screen_name="pictestempt").pics.order_by("-date")[4].id
# profile = Profile.objects.get(screen_name="dank_exe").pics.order_by("-date")[27].id
# profile = Profile.objects.get(screen_name="karkb").pics.order_by("-date")[16].id
# profile = Profile.objects.get(screen_name__startswith="teacheng").pics.order_by("-date")[15].id
# profile = Profile.objects.get(screen_name__startswith="afroside").pics.order_by("-date")[29].id

# profile = Profile.objects.get(screen_name__startswith="dvj_prj")

profile = Profile.objects.get(user=User.objects.get(email="kabakov_ivan2@mail.ru"))

ctr = Ticket.objects.filter(profile=profile, is_issued=True, is_returned=False).count()

print(ctr)
