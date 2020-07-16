from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.shortcuts import redirect
from .models import Meme, Profile
from django.contrib.auth.models import User
from .picture_saver import meme_json_parser

from .config import Secrets, Config

secrets = Secrets()
config = Config()


def construct_app_response(status, content):
    response = {
        "status": status,
        "content": content,
    }
    return JsonResponse(response)


def share_picture(request, club_id, source_name):
    context = {"image_url": f"{config['image_server_url']}/{club_id}/{source_name}"}
    template = loader.get_template("void_app/share.html")
    return HttpResponse(template.render(context))


def subscription_picture_app(request):
    profile = log_in_user(request)
    if does_exist_unseen_subscription_picture(profile):
        meme = subscription_picture(profile)
        answer = {
            "picture_url": f"{config['image_server_url']}{meme.picture_url}",
            "like_number": meme.likes,
            "picture_id": meme.id,
            "like_url": f"{config['main_server_url']}/like_picture/{meme.id}",
        }
        return construct_app_response("ok", answer)
    else:
        return construct_app_response("all sub pic seen", None)


def random_picture_app(request):
    profile = log_in_user(request)
    meme = random_picture(profile)
    answer = {
        "picture_url": f"{config['image_server_url']}{meme.picture_url}",
        "like_number": meme.likes,
        "picture_id": meme.id,
        "like_url": f"{config['main_server_url']}/like_picture/{meme.id}",
    }
    return construct_app_response("ok", answer)


def view_random_picture_url(request):
    profile = log_in_user(request)
    meme = random_picture(profile)
    return redirect(f"{config['image_server_url']}{meme.picture_url}")


def view_random_picture(request):
    profile = log_in_user(request)
    meme = random_picture(profile)
    template = loader.get_template('void_app/feed.html')
    context = {
        'meme': meme,
        'main_server_url': config["main_server_url"],
        'picture_server_url': config["image_server_url"]
    }
    return HttpResponse(template.render(context))


def view_subscription_picture(request):
    profile = log_in_user(request)
    meme = subscription_picture(profile)
    template = loader.get_template('void_app/feed.html')
    context = {
        'meme': meme,
        'main_server_url': config["main_server_url"],
        'picture_server_url': config["image_server_url"]
    }
    return HttpResponse(template.render(context))


def view_random_picture_mobile(request):
    profile = log_in_user(request)
    meme = random_picture(profile)
    template = loader.get_template('void_app/feed_mobile.html')
    context = {
        'meme': meme,
        'main_server_url': config["main_server_url"],
        'picture_server_url': config["image_server_url"]
    }
    return HttpResponse(template.render(context))


def does_exist_unseen_subscription_picture(profile):
    if Meme.objects.filter(club__sub_profile=profile).exclude(seen_profile=profile).order_by("?"):
        return True
    else:
        return False


def subscription_picture(profile):
    meme = Meme.objects.filter(club__sub_profile=profile).exclude(seen_profile=profile).order_by("?").first()
    profile.seen_memes.add(meme)
    return meme


def random_picture(profile):
    meme = Meme.objects.exclude(seen_profile=profile).order_by("?").first()
    profile.seen_memes.add(meme)
    return meme


def get_random_object_by_type(object_type):
    return object_type.objects.order_by("?").first()


def switch_like(request, meme_id):
    profile = log_in_user(request)
    meme = Meme.objects.filter(id=meme_id).first()
    if not profile.liked_memes.filter(id=meme_id).exists():
        meme.add_like()
        profile.liked_memes.add(meme)
    else:
        meme.remove_like()
        profile.liked_memes.remove(meme)
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def update_memes_db(request):
    post_json = request.POST["archive"]
    meme_json_parser(post_json)
    return JsonResponse({'status': 'ok'})


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_in_user(request):
    ip = get_user_ip(request)
    if not Profile.objects.filter(ip=ip).first():
        new_user = User.objects.create_user(str(randint(1, 100000000000)))
        new_user.save()
        profile = Profile()
        profile.add_ip(ip)
        profile.user = new_user
        profile.save()
    return Profile.objects.filter(ip=ip).first()
