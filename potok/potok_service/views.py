import base64
from itertools import chain
from random import randint

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .config import Secrets, Config
from .functions import id_gen, token_from_id, id_from_token
from .importer import pics_json_parser, profiles_json_parser, pic_upload
from .models import Picture, Profile, Session, Like, Subscription, View, CustomAnonymousUser, CustomUser, Link

secrets = Secrets()
config = Config()


def login_user(func):
    def wrapper(request, *args, **kwargs):
        profile = profile_by_token(request)
        return func(request, profile, *args, **kwargs)

    return wrapper


def construct_app_response(status, content):
    response = {
        "status": status,
        "content": content,
    }
    return JsonResponse(response)


# def share_picture(request, club_id, source_name):
#     context = {"image_url": f"{config['image_server_url']}/{club_id}/{source_name}"}
#     template = loader.get_template("potok_service/share.html")
#     return HttpResponse(template.render(context))


def create_session(profile):
    for session in Session.objects.filter(profile=profile, is_opened=True):
        session.is_opened = False
        session.save()
    session = Session.objects.create(profile=profile, is_opened=True, token=id_gen(20))
    return session


@login_user
def create_session_request(request, user_profile):
    session = create_session(user_profile)
    answer = {
        "session_token": session.token,
    }
    return construct_app_response("ok", answer)


@login_user
def app_subscription_pictures(request, user_profile, session_token, number):
    session = Session.objects.get(token=session_token)
    pictures = subscription_pictures(user_profile, session, number)
    response_content = list(map(lambda pic: construct_picture_response(pic, user_profile), pictures))
    return construct_app_response("ok", response_content)


@login_user
def app_feed_pictures(request, user_profile, session_token, number):
    session = Session.objects.get(token=session_token)
    pictures = feed_pictures(user_profile, session, number)
    response_content = list(map(lambda pic: construct_picture_response(pic, user_profile), pictures))
    return construct_app_response("ok", response_content)


@login_user
def app_my_profile(request, user_profile):
    response_content = construct_profile_response(user_profile, user_profile)
    return construct_app_response("ok", response_content)


def construct_picture_response(pic: Picture, user_profile: Profile = None):
    answer = {
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
    return answer


def construct_profile_response(profile: Profile, user_profile: Profile = None):
    answer = {
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
    return answer


@login_user
def profile_pictures(request, user_profile, profile_id, number=10, offset=0):
    pics = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:offset + number]
    answer = list(map(lambda pic: construct_picture_response(pic, user_profile), pics))
    return construct_app_response("ok", answer)


@csrf_exempt
@login_user
def upload_picture(request, user_profile):
    picture_data = base64.b64decode(request.POST["picture"])
    pic_upload(picture_data, user_profile, request.POST["extension"])
    return JsonResponse({'status': 'ok'})


def does_exist_unseen_subscription_picture(profile: Profile):
    if Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exists():
        return True
    else:
        return False


def subscription_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.sub_pics.add(picture)
        session.save()
    return pictures


def feed_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.feed_pics.add(picture)
        session.save()
    return pictures


@login_user
def switch_like(request, user_profile, pic_id):
    picture = Picture.objects.get(id=pic_id)
    if Like.objects.filter(picture=picture, profile=user_profile).exists():
        Like.objects.get(picture=picture, profile=user_profile).delete()
        picture.likes_num -= max(0, picture.likes_num - 1)
    else:
        Like.objects.create(picture=picture, profile=user_profile)
        picture.likes_num += 1
    picture.save()
    return JsonResponse({'status': 'ok'})


@login_user
def switch_subscribe(request, user_profile, sub_profile_id):
    sub_profile = Profile.objects.get(id=sub_profile_id)
    if Subscription.objects.filter(follower=user_profile, source=sub_profile).exists():
        Subscription.objects.get(follower=user_profile, source=sub_profile).delete()
    else:
        Subscription.objects.create(follower=user_profile, source=sub_profile)
    user_profile.save()
    return JsonResponse({'status': 'ok'})


@login_user
def mark_as_seen(request, user_profile, pic_id):
    picture = Picture.objects.get(id=pic_id)
    View.objects.create(picture=picture, profile=user_profile)
    return JsonResponse({'status': 'ok'})


def construct_subscription_response(user_profile, subscription):
    answer = {
        "type": "subscription",
        "profile": construct_profile_response(subscription.follower, user_profile),
        "date": int(subscription.date.timestamp()),
    }
    return answer


def construct_like_response(user_profile, like):
    answer = {
        "type": "like",
        "profile": construct_profile_response(like.profile, user_profile),
        "picture": construct_picture_response(like.picture, user_profile),
        "date": int(like.date.timestamp()),
    }
    return answer


def construct_action(user_profile, action):
    if isinstance(action, Like):
        return construct_like_response(user_profile, action)
    elif isinstance(action, Subscription):
        return construct_subscription_response(user_profile, action)


@login_user
def generate_profile_share_link(request, user_profile, profile_id):
    profile = Profile.objects.filter(id=profile_id).first()
    link = Link.objects.create(sender=user_profile, content_type=ContentType.objects.get_for_model(profile), content=profile)
    share_token = token_from_id(link.id)
    answer = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
    return construct_app_response("ok", answer)


@login_user
def generate_picture_share_link(request, user_profile, pic_id):
    picture = Picture.objects.filter(id=pic_id).first()
    link = Link.objects.create(sender=user_profile, content_type=ContentType.objects.get_for_model(picture), content=picture)
    share_token = token_from_id(link.id)
    answer = {"share_url": f"{config['main_server_url']}/share/{share_token}"}
    return construct_app_response("ok", answer)


def get_content_by_link(request, share_token):
    link = Link.objects.filter(id=id_from_token(share_token)).first()
    if isinstance(link.content, Picture):
        answer = construct_picture_response(link.content)
        return render(request, 'potok_service/share.html', {"picture": answer})
    elif isinstance(link.content, Profile):
        answer = construct_profile_response(link.content)
        return construct_app_response("ok", answer)
    return construct_app_response("Not found", None)

@login_user
def last_actions(request, user_profile, number, offset):
    likes = Like.objects.filter(picture__profile=user_profile).order_by('-date')[:offset + number]
    subscriptions = Subscription.objects.filter(source=user_profile).order_by('-date')[:offset + number]
    actions = list(sorted(chain(likes, subscriptions), key=lambda action: action.date))[offset:offset + number]
    answer = [construct_action(user_profile, action) for action in actions]
    return construct_app_response("ok", answer)


@csrf_exempt
def update_pics_db(request):
    post_json = request.POST["archive"]
    pics_json_parser(post_json)
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def update_profiles_db(request):
    post_json = request.POST["archive"]
    profiles_json_parser(post_json)
    return JsonResponse({'status': 'ok'})


def get_device_id(request):
    if request.method == "GET":
        return request.GET["device_id"]
    elif request.method == "POST":
        return request.POST["device_id"]
    else:
        raise ValueError("Request has no attribute 'device_id'")


def get_token(request):
    if request.method == "GET":
        return request.GET["auth_token"]
    elif request.method == "POST":
        return request.POST["auth_token"]
    else:
        return ValueError("Request has no attribute 'token'")


def profile_by_token(request) -> Profile:
    token = get_token(request)
    if CustomAnonymousUser.objects.filter(token=token).exists():
        anonymous_user = CustomAnonymousUser.objects.filter(token=token).first()
        return anonymous_user.profile
    elif CustomUser.objects.filter(token=token).exists():
        user = CustomUser.objects.filter(token=token).first()
        return user.profile
    else:
        raise ValueError("User with this token was not found")


def log_in_via_device_id(request):
    device_id = get_device_id(request)
    if not CustomAnonymousUser.objects.filter(device_id=device_id).exists():
        random_int = randint(1, 100000000000)
        anonymous_user = CustomAnonymousUser(
            id=str(random_int),
            device_id=device_id,
            token=id_gen(80),
            username=random_int,
        )
        # anonymous_user.id = str(randint(1, 100000000000))
        profile = Profile(
            user=anonymous_user,
        )
        anonymous_user.save()
        profile.save()
        return construct_app_response("ok", {"auth_token": anonymous_user.token})
    else:
        return construct_app_response(
            "ok",
            {"auth_token": CustomAnonymousUser.objects.filter(device_id=device_id).first().token},
        )
