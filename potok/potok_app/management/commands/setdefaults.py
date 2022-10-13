from django.core.management.base import BaseCommand, CommandError

from potok.settings import STATIC_ROOT
from potok_app.models import Profile
from potok_app.services.picture.avatar import create_avatar


class Command(BaseCommand):
    help = 'Set defaults values as avatar'

    def handle(self, *args, **options):
        empty_profile = Profile()
        empty_profile.save()

        path_to_default_avatar = f'{STATIC_ROOT}/extra/default_avatar.png'
        try:
            picture_bytes = open(path_to_default_avatar, 'rb').read()
            avatar = create_avatar(empty_profile, picture_bytes, extension=path_to_default_avatar.split('.')[-1])
        except Exception as e:
            raise CommandError(f'Failed to initialize default avatar {e}')

        self.stdout.write(self.style.SUCCESS(f'Defaults initialized, avatar id is {avatar}'))
