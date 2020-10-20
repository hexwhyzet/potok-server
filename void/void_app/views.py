from random import randint

from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .config import Secrets, Config
from .functions import id_gen
from .importer import pics_json_parser, profiles_json_parser
from .models import Picture, Profile, Session

secrets = Secrets()
config = Config()


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


def create_session_request(request):
    profile = log_in_user(request)
    session = create_session(profile)
    answer = {
        "token": session.token,
    }
    return construct_app_response("ok", answer)


def app_subscription_picture(request, session_token):
    profile = log_in_user(request)
    if does_exist_unseen_subscription_picture(profile):
        session = Session.objects.get(token=session_token)
        picture = subscription_picture(profile, session)
        response_content = construct_picture_response(profile, picture)
        return construct_app_response("ok", response_content)
    else:
        return construct_app_response("all sub pic seen", None)


def app_feed_picture(request, session_token):
    profile = log_in_user(request)
    session = Session.objects.get(token=session_token)
    picture = feed_picture(profile, session)
    response_content = construct_picture_response(profile, picture)
    return construct_app_response("ok", response_content)


def app_my_profile(request):
    profile = log_in_user(request)
    response_content = construct_profile_response(profile, profile)
    return construct_app_response("ok", response_content)


def construct_picture_response(user_profile: Profile, pic: Picture):
    answer = {
        "id": pic.id,
        "url": f"{config['image_server_url']}{pic.url}",
        "res": pic.res,
        "date": pic.date,
        "views_num": pic.views_num,
        "likes_num": pic.likes_num,
        "shares_num": pic.shares_num,
        "like_url": f"{config['main_server_url']}/like_picture/{pic.id}",
        "profile": construct_profile_response(user_profile, pic.profile)
    }
    return answer


def construct_profile_response(user_profile: Profile, profile: Profile):
    answer = {
        "id": profile.id,
        "name": profile.name or "unknown",
        "screen_name": profile.screen_name or "unknown",
        "subs_num": profile.subs.count(),
        "followers_num": profile.followers.count(),
        "views_num": profile.pics.aggregate(views_num=Coalesce(Sum('views_num'), 0))['views_num'],
        "likes_num": profile.pics.aggregate(likes_num=Coalesce(Sum('likes_num'), 0))['likes_num'],
        "avatar_url": f"{config['image_server_url']}{profile.avatar_url or '/defaults/avatar.jpg'}",
        "is_subscribed": user_profile.subs.filter(id=profile.id).exists(),
        "subscribe_url": f"{config['main_server_url']}/subscribe/{profile.id}",
        "is_yours": profile == user_profile,
    }
    return answer


def profile_pictures(request, profile_id, number=10, offset=0):
    profile = log_in_user(request)
    pics_num = Picture.objects.filter(profile__id=profile_id).count()
    if pics_num <= offset:
        return construct_app_response("no more pictures", [])
    elif pics_num >= number + offset:
        pics = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:offset + number]
    else:
        pics = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:]
    answer = list(map(lambda pic: construct_picture_response(profile, pic), pics))
    return construct_app_response("ok", answer)


# def view_random_picture_url(request):
#     profile = log_in_user(request)
#     meme = random_picture(profile)
#     return redirect(f"{config['image_server_url']}{meme.picture_url}")
#
#
# def view_random_picture(request):
#     profile = log_in_user(request)
#     meme = random_picture(profile)
#     template = loader.get_template('void_app/feed.html')
#     context = {
#         'meme': meme,
#         'main_server_url': config["main_server_url"],
#         'picture_server_url': config["image_server_url"]
#     }
#     return HttpResponse(template.render(context))


# def view_subscription_picture(request):
#     profile = log_in_user(request)
#     meme = subscription_picture(profile)
#     template = loader.get_template('void_app/feed.html')
#     context = {
#         'meme': meme,
#         'main_server_url': config["main_server_url"],
#         'picture_server_url': config["image_server_url"]
#     }
#     return HttpResponse(template.render(context))
#
#
# def view_random_picture_mobile(request):
#     profile = log_in_user(request)
#     meme = random_picture(profile)
#     template = loader.get_template('void_app/feed_mobile.html')
#     context = {
#         'meme': meme,
#         'main_server_url': config["main_server_url"],
#         'picture_server_url': config["image_server_url"]
#     }
#     return HttpResponse(template.render(context))


def does_exist_unseen_subscription_picture(profile: Profile):
    if Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exists():
        return True
    else:
        return False


def subscription_picture(profile: Profile, session: Session):
    picture = Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).latest("date")
    picture.views_num += 1
    picture.save()
    profile.pics_viewed.add(picture)
    profile.save()
    session.sub_pics.add(picture)
    session.save()
    return picture


def feed_picture(profile: Profile, session: Session):
    picture = Picture.objects.exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).latest("date")
    picture.views_num += 1
    picture.save()
    profile.pics_viewed.add(picture)
    profile.save()
    session.feed_pics.add(picture)
    session.save()
    return picture


def switch_like(request, pic_id):
    user_profile = log_in_user(request)
    picture = Picture.objects.filter(id=pic_id).first()
    if not user_profile.pics_liked.filter(id=pic_id).exists():
        user_profile.pics_liked.add(picture)
        picture.likes_num += 1
    else:
        user_profile.pics_liked.remove(picture)
        picture.likes_num -= 1
    picture.save()
    return JsonResponse({'status': 'ok'})


def subscribe(request, club_id):
    profile = log_in_user(request)
    profile.subs.add(club_id)
    return JsonResponse({'status': 'ok'})


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


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_in_user(request) -> Profile:
    ip = get_user_ip(request)
    if not Profile.objects.filter(ip=ip).first():
        new_user = User.objects.create_user(str(randint(1, 100000000000)))
        new_user.save()
        profile = Profile()
        profile.ip = ip
        profile.user = new_user
        profile.save()
    return Profile.objects.filter(ip=ip).first()
