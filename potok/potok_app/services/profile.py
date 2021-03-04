from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.db.models import Count

from potok_app.config import Secrets, Config
from potok_app.functions import id_gen
from potok_app.models import Profile, Avatar, AvatarData, ProfileBlock
from potok_app.object_storage_api import upload_picture
from potok_app.picture_resizer import resize_and_compress

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

    name_rank = SearchRank(SearchVector('name'), SearchQuery(text)) * 8

    trigram_similarity = TrigramSimilarity('screen_name', text)

    return Profile.objects.annotate(rank=name_rank + trigram_similarity).filter(
        rank__gt=0.25).order_by('-rank')[offset:offset + number]


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


def add_avatar(profile, raw_avatar_data, extension, source_url=None):
    if source_url is not None:
        avatar, _ = Avatar.objects.get_or_create(profile=profile, source_url=source_url)
    else:
        avatar = Avatar.objects.create(profile=profile)
    resize_and_upload_avatar_to_storage(avatar, raw_avatar_data, extension, [200])


def resize_and_upload_avatar_to_storage(avatar, raw_picture_data, extension, widths=None):
    for res, resized_picture in resize_and_compress(raw_picture_data, extension, widths).items():
        url = upload_picture(resized_picture, f'{config["image_server_directory"]}/{id_gen(50)}.{extension}')
        picture_data, _ = AvatarData.objects.get_or_create(avatar=avatar, res=res, url=url)


def switch_block(blocker, blocked):
    if ProfileBlock.objects.filter(blocked=blocked).exists():
        ProfileBlock.objects.filter(blocked=blocked).delete()
    else:
        ProfileBlock.objects.create(blocker=blocker, blocked=blocked)


def update_screen_name(profile: Profile, screen_name: str):
    profile.screen_name = screen_name
    profile.save()


def update_name(profile: Profile, name: str):
    profile.name = name
    profile.save()


def does_screen_name_exists(screen_name: str):
    return Profile.objects.filter(screen_name=screen_name).exists()


def update_publicity(profile: Profile, is_public: bool):
    profile.is_public = is_public
    profile.save()


def update_liked_pictures_publicity(profile: Profile, are_liked_pictures_public: bool):
    profile.are_liked_pictures_public = are_liked_pictures_public
    profile.save()


def trending_profiles(number, offset):
    profiles = Profile.objects.annotate(pics_num=Count('pics')).filter(pics_num__gt=0).annotate(
        trend_rank=Count('followers')).order_by('-trend_rank').all()[offset:offset + number]
    return profiles
