from random_username.generate import generate_username

from potok_app.models import Profile
from potok_app.services.profile.profile_block import does_block_exist
from potok_app.services.profile.profile_subscription import does_subscription_exist, get_subscription, \
    does_subscription_exist_and_accepted


def available_profiles():
    return Profile.objects.all()


def does_profile_exist(profile_id):
    return Profile.objects.filter(id=profile_id).exists()


def profile_by_id(profile_id):
    return Profile.objects.get(id=profile_id)


def is_blocked(profile_blocker: Profile, profile_blocked: Profile):
    return profile_blocker.blocked_profiles.filter(id=profile_blocked.id).exists()


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
           and (not requested_profile.is_private or does_subscription_exist_and_accepted(requester_profile,
                                                                                         requested_profile))


def is_liked_pictures_page_available(requester_profile: Profile, requested_profile: Profile):
    if is_profile_users(requester_profile, requested_profile):
        return True

    if is_profile_content_available(requester_profile, requested_profile) \
            and not requested_profile.are_liked_pictures_private:
        return True

    return False


def get_block_status(requester_profile: Profile, requested_profile: Profile):
    if is_profile_users(requester_profile, requested_profile):
        return -1

    if not is_blocked(requester_profile, requested_profile) and not is_blocked(requested_profile, requester_profile):
        return 0

    if is_blocked(requester_profile, requested_profile) and not is_blocked(requested_profile, requester_profile):
        return 1

    if not is_blocked(requester_profile, requested_profile) and is_blocked(requested_profile, requester_profile):
        return 2

    if is_blocked(requester_profile, requested_profile) and is_blocked(requested_profile, requester_profile):
        return 3

    return 0


def get_subscription_status(requester_profile: Profile, requested_profile: Profile):
    if is_profile_users(requester_profile, requested_profile):
        return -1
    if does_subscription_exist(requester_profile, requested_profile):
        if not get_subscription(requester_profile, requested_profile).is_accepted:
            return 1
        else:
            return 2

    return 0
