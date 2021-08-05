from random_username.generate import generate_username

from potok_app.models import Profile
from potok_app.services.profile.profile_block import does_block_exist
from potok_app.services.profile.profile_subscription import does_subscription_exist


def available_profiles():
    return Profile.objects.all()


def profile_by_id(profile_id):
    return Profile.objects.get(id=profile_id)


def is_blocked(profile1: Profile, profile2: Profile):
    return profile1.blocked_profiles.filter(id=profile2.id).exists()


def followers(profile: Profile):
    return profile.followers.all()


def leaders(profile: Profile):
    return profile.sub_leaders.all()


def generate_unique_screen_name():
    screen_name = generate_username()[0]
    while Profile.objects.filter(screen_name=screen_name).exists():
        screen_name = generate_username()[0]
    return screen_name


def is_profile_users(user_profile: Profile, profile: Profile):
    return user_profile == profile


def is_profile_content_available(requester_profile: Profile, requested_profile: Profile):
    if is_profile_users(requester_profile, requested_profile):
        return True

    return not does_block_exist(requester_profile, requested_profile) \
           and not does_block_exist(requester_profile, requested_profile) \
           and (requested_profile.is_public or does_subscription_exist(requester_profile, requested_profile))
