import base64
from itertools import chain
from random import randint

from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .config import Secrets, Config
from .functions import id_gen
from .importer import pics_json_parser, profiles_json_parser, pic_upload
from .models import Picture, Profile, Session, Like, Subscription, View, CustomAnonymousUser

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
#     template = loader.get_template("void_app/share.html")
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
    response_content = list(map(lambda pic: construct_picture_response(user_profile, pic), pictures))
    return construct_app_response("ok", response_content)


@login_user
def app_feed_pictures(request, user_profile, session_token, number):
    session = Session.objects.get(token=session_token)
    pictures = feed_pictures(user_profile, session, number)
    response_content = list(map(lambda pic: construct_picture_response(user_profile, pic), pictures))
    return construct_app_response("ok", response_content)


@login_user
def app_my_profile(request, user_profile):
    response_content = construct_profile_response(user_profile, user_profile)
    return construct_app_response("ok", response_content)


def construct_picture_response(user_profile: Profile, pic: Picture):
    answer = {
        "id": pic.id,
        "type": "picture",
        "url": f"{config['image_server_url']}{pic.url}",
        "res": pic.res,
        "date": pic.date,
        "views_num": pic.views_num,
        "likes_num": pic.likes_num,
        "shares_num": pic.shares_num,
        "is_liked": pic.profiles_liked.filter(id=user_profile.id).exists(),
        "like_url": f"{config['main_server_url']}/app/like_picture/{pic.id}",
        "profile": construct_profile_response(user_profile, pic.profile)
    }
    return answer


def construct_profile_response(user_profile: Profile, profile: Profile):
    answer = {
        "id": profile.id,
        "type": "profile",
        "name": profile.name or "unknown",
        "screen_name": profile.screen_name or "unknown",
        "subs_num": profile.subs.count(),
        "followers_num": profile.followers.count(),
        "views_num": profile.pics.aggregate(views_num=Coalesce(Sum('views_num'), 0))['views_num'],
        "likes_num": profile.pics.aggregate(likes_num=Coalesce(Sum('likes_num'), 0))['likes_num'],
        "avatar_url": f"{config['image_server_url']}{profile.avatar_url or '/defaults/avatar.jpg'}",
        "is_subscribed": user_profile.subs.filter(id=profile.id).exists(),
        "subscribe_url": f"{config['main_server_url']}/app/subscribe/{profile.id}",
        "is_yours": profile == user_profile,
    }
    return answer


@login_user
def profile_pictures(request, user_profile, profile_id, number=10, offset=0):
    pics = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:offset + number]
    answer = list(map(lambda pic: construct_picture_response(user_profile, pic), pics))
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
        picture.likes_num += 1
    else:
        Like.objects.create(picture=picture, profile=user_profile)
        picture.likes_num -= 1
    user_profile.save()
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


def construct_subscription_response(subscription):
    answer = {
        "type": "subscription",
        "profile": construct_profile_response(subscription.follower),
        "date": subscription.date,
    }
    return answer


def construct_like_response(like):
    answer = {
        "type": "like",
        "profile": construct_profile_response(like.follower),
        "date": like.date,
    }
    return answer


def construct_action(action):
    if type(action) == "Like":
        return construct_like_response(action)
    elif type(action) == "Subscription":
        return construct_subscription_response(action)


@login_user
def last_actions(request, user_profile, number, offset):
    likes = Like.objects.filter(profile=user_profile).order_by('-date')[:offset + number]
    subscriptions = Subscription.objects.filter(profile=user_profile).order_by('-date')[:offset + number]
    actions = list(sorted(chain(likes, subscriptions), key=lambda action: action.date))[offset:offset + number]
    answer = [construct_action(action) for action in actions]
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
    if not CustomAnonymousUser.objects.filter(token=token).exists():
        anonymous_user = CustomAnonymousUser.objects.filter(token=token).first()
        return anonymous_user.profile
    else:
        raise ValueError("User with this token was not found")


def log_in_via_device_id(request):
    device_id = get_device_id(request)
    if not CustomAnonymousUser.objects.filter(device_id=device_id).exists():
        anonymous_user = CustomAnonymousUser(
            id=str(randint(1, 100000000000)),
            device_id=device_id,
            token=id_gen(80),
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
