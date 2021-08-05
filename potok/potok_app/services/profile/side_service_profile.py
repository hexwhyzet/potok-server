from potok_app.models import Profile


def get_or_create_side_service_profile(minor_id: str):
    return Profile.objects.get_or_create(minor_id=minor_id)


def update_or_create_side_service_profile(minor_id: str, name: str, screen_name: str):
    Profile.objects.update_or_create(
        minor_id=minor_id,
        defaults={
            "name": name,
            "screen_name": screen_name,
        })
