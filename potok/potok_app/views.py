import base64

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from potok_app.config import Secrets, Config
from potok_app.importer import pics_json_parser, profiles_json_parser, pic_upload
from potok_app.models import Picture, Profile, Like, Subscription
from potok_app.services.actions import switch_like, last_actions, add_view, switch_subscription
from potok_app.services.authorizer import login_user, get_device_id, anonymous_user_exist, \
    create_anonymous_user, anonymous_user_by_device_id
from potok_app.services.link import link_by_share_token, create_link, share_token_by_link
from potok_app.services.picture import subscription_pictures, feed_pictures, profile_pictures, \
    picture_by_id
from potok_app.services.profile import profile_by_id, search_profiles_by_screen_name_prefix, search_profiles_by_text
from potok_app.services.session import create_session, session_by_token

secrets = Secrets()
config = Config()


def construct_app_response(status, content):
    response = {
        "status": status,
        "content": content,
    }
    return JsonResponse(response)


def construct_picture_response(pic: Picture, user_profile: Profile = None):
    response_content = {
        "id": pic.id,
        "type": "picture",
        "url": f"{config['image_server_url']}{pic.url}",
        "res": pic.res,
        "date": pic.date,
        "views_num": pic.views_num,
        "likes_num": pic.likes_num,
        "shares_num": pic.shares_num,
        "is_liked": pic.profiles_liked.filter(id=user_profile.id).exists() if user_profile is not None else None,
        "like_url": f"{config['main_server_url']}/app/like_picture/{pic.id}",
        "share_url": f"{config['main_server_url']}/app/share_picture/{pic.id}",
        "profile": construct_profile_response(pic.profile, user_profile)
    }
    return response_content


def construct_pictures(pictures: list[Picture], user_profile: Profile = None):
    pictures = [construct_picture_response(picture, user_profile) for picture in pictures]
    return pictures


def construct_profile_response(profile: Profile, user_profile: Profile = None):
    response_content = {
        "id": profile.id,
        "type": "profile",
        "name": profile.name or "unknown",
        "screen_name": profile.screen_name or "unknown",
        "subs_num": profile.subs.count() if user_profile is not None else None,
        "followers_num": profile.followers.count(),
        "views_num": profile.pics.aggregate(views_num=Coalesce(Sum('views_num'), 0))['views_num'],
        "likes_num": profile.pics.aggregate(likes_num=Coalesce(Sum('likes_num'), 0))['likes_num'],
        "avatar_url": f"{config['image_server_url']}{profile.avatar_url or '/defaults/avatar.png'}",
        "is_subscribed": user_profile.subs.filter(id=profile.id).exists() if user_profile is not None else None,
        "subscribe_url": f"{config['main_server_url']}/app/subscribe/{profile.id}",
        "share_url": f"{config['main_server_url']}/app/share_profile/{profile.id}",
        "is_yours": profile == user_profile,
    }
    return response_content


def construct_profiles(profiles: list[Profile], user_profile: Profile = None):
    profiles = [construct_profile_response(profile, user_profile) for profile in profiles]
    return profiles


def construct_subscription_response(user_profile, subscription):
    response_content = {
        "type": "subscription",
        "profile": construct_profile_response(subscription.follower, user_profile),
        "date": int(subscription.date.timestamp()),
    }
    return response_content


def construct_like_response(user_profile, like):
    response_content = {
        "type": "like",
        "profile": construct_profile_response(like.profile, user_profile),
        "picture": construct_picture_response(like.picture, user_profile),
        "date": int(like.date.timestamp()),
    }
    return response_content


def construct_action(user_profile, action):
    if isinstance(action, Like):
        return construct_like_response(user_profile, action)
    elif isinstance(action, Subscription):
        return construct_subscription_response(user_profile, action)


@login_user
def app_create_session_request(request, user_profile):
    session = create_session(user_profile)
    response_content = {
        "session_token": session.token,
    }
    return construct_app_response("ok", response_content)


@login_user
def app_subscription_pictures(request, user_profile, session_token, number):
    session = session_by_token(session_token)
    pictures = subscription_pictures(user_profile, session, number)
    response_content = construct_pictures(pictures, user_profile)
    return construct_app_response("ok", response_content)


@login_user
def app_feed_pictures(request, user_profile, session_token, number):
    session = session_by_token(session_token)
    pictures = feed_pictures(user_profile, session, number)
    response_content = construct_pictures(pictures, user_profile)
    return construct_app_response("ok", response_content)


@login_user
def app_my_profile(request, user_profile):
    response_content = construct_profile_response(user_profile, user_profile)
    return construct_app_response("ok", response_content)


@login_user
def app_profile_pictures(request, user_profile, profile_id, number=10, offset=0):
    pictures = profile_pictures(profile_id, number, offset)
    response_content = construct_pictures(pictures, user_profile)
    return construct_app_response("ok", response_content)


@csrf_exempt
@login_user
def app_upload_picture(request, user_profile):
    picture_data = base64.b64decode(request.POST["picture"])
    pic_upload(picture_data, user_profile, request.POST["extension"])
    return construct_app_response("ok", None)


@login_user
def app_switch_like(request, user_profile, picture_id):
    picture = picture_by_id(picture_id)
    switch_like(user_profile, picture)
    return construct_app_response("ok", None)


@login_user
def app_switch_subscription(request, user_profile, sub_profile_id):
    sub_profile = Profile.objects.get(id=sub_profile_id)
    switch_subscription(user_profile, sub_profile)
    return construct_app_response("ok", None)


@login_user
def app_add_view(request, user_profile, picture_id):
    add_view(user_profile, picture_by_id(picture_id))
    return construct_app_response("ok", None)


@login_user
def app_generate_profile_share_link(request, user_profile, profile_id):
    profile = profile_by_id(profile_id)
    link = create_link(user_profile, profile)
    share_token = share_token_by_link(link)
    response_content = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
    return construct_app_response("ok", response_content)


@login_user
def app_generate_picture_share_link(request, user_profile, picture_id):
    picture = picture_by_id(picture_id)
    link = create_link(user_profile, picture)
    share_token = share_token_by_link(link)
    response_content = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
    return construct_app_response("ok", response_content)


@login_user
def app_last_actions(request, user_profile, number, offset):
    actions = last_actions(user_profile, number, offset)
    response_content = [construct_action(user_profile, action) for action in actions]
    return construct_app_response("ok", response_content)


def app_autofill(request, search_string, number, offset):
    profiles = search_profiles_by_screen_name_prefix(search_string, number, offset)
    response_content = construct_profiles(profiles)
    return construct_app_response("ok", response_content)


def app_search(request, search_string, number, offset):
    profiles = search_profiles_by_text(search_string, number, offset)
    response_content = construct_profiles(profiles)
    return construct_app_response("ok", response_content)


@csrf_exempt
def update_pictures_db(request):
    post_json = request.POST["archive"]
    pics_json_parser(post_json)
    return construct_app_response("ok", None)


@csrf_exempt
def update_profiles_db(request):
    post_json = request.POST["archive"]
    profiles_json_parser(post_json)
    return construct_app_response("ok", None)


def content_by_link(request, share_token: str):
    link = link_by_share_token(share_token)
    if isinstance(link.content, Picture):
        response_content = construct_picture_response(link.content)
        return render(request, 'share.html', {"picture": response_content})
    elif isinstance(link.content, Profile):
        response_content = construct_profile_response(link.content)
        return construct_app_response("ok", response_content)
    else:
        return HttpResponseNotFound("Meme not Found :(")


def log_in_via_device_id(request):
    device_id = get_device_id(request)
    if not anonymous_user_exist(device_id):
        anonymous_user = create_anonymous_user(device_id)
    else:
        anonymous_user = anonymous_user_by_device_id(device_id)
    return construct_app_response("ok", {"auth_token": anonymous_user.token})
