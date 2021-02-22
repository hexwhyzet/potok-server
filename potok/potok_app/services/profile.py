from django.contrib.postgres.search import TrigramSimilarity

from potok_app.config import Secrets, Config
from potok_app.functions import id_gen
from potok_app.models import Profile, Avatar, AvatarData, ProfileBlock
from potok_app.object_storage_api import upload_picture

secrets = Secrets()
config = Config()


def profile_by_id(profile_id):
    return Profile.objects.get(id=profile_id)


def search_profiles_by_screen_name_prefix(prefix, number, offset):
    return Profile.objects.filter(screen_name__istartswith=prefix)[offset:offset + number]


# def search_profiles_by_text(text, number, offset):
#     vector = SearchVector('name', 'screen_name')
#     query = SearchQuery(text)
#     return Profile.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.3).order_by('rank')[
#            offset:offset + number]

def search_profiles_by_text(text, number, offset):
    return Profile.objects.annotate(similarity=TrigramSimilarity('screen_name', text)) \
               .filter(similarity__gt=0.25).order_by('-similarity')[offset:offset + number]


def are_friends(profile1: Profile, profile2: Profile):
    return profile1 in profile2.subs and profile2 in profile1.subs


def is_blocked_by_user(user_profile: Profile, profile: Profile):
    return user_profile.blocked_profiles.filter(id=profile.id).exists()


def is_profile_yours(user_profile: Profile, profile: Profile):
    return user_profile == profile


def is_profile_available(user_profile: Profile, profile: Profile):
    if is_profile_yours(user_profile, profile):
        return True

    return not is_blocked_by_user(user_profile, profile) \
           and not is_blocked_by_user(profile, user_profile) \
           and (profile.is_public or are_friends(user_profile, profile))


def are_liked_pictures_available(user_profile: Profile, profile: Profile):
    if is_profile_yours(user_profile, profile):
        return True

    return is_profile_available(user_profile, profile) and profile.are_liked_pictures_public


def latest_avatar(profile: Profile):
    if profile.avatars.exists():
        return profile.avatars.latest('id')
    else:
        return None


def avatar_url(profile: Profile):
    avatar = latest_avatar(profile)
    if avatar is not None:
        return avatar.avatar_data.latest('res').url
    else:
        return None


def add_avatar(profile, raw_avatar_data, extension, res=None, source_url=None):
    avatar, _ = Avatar.objects.get_or_create(profile=profile, source_url=source_url)
    url = upload_picture(raw_avatar_data, f'{config["image_server_directory"]}/{id_gen(50)}.{extension}')
    AvatarData.objects.create(avatar=avatar, url=url, res=res)


def switch_block(blocker, blocked):
    if ProfileBlock.objects.filter(blocked=blocked).exists():
        ProfileBlock.objects.filter(blocked=blocked).delete()
    else:
        ProfileBlock.objects.create(blocker=blocker, blocked=blocked)
