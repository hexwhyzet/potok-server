from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from random import randint

from .models import Meme, Profile
from django.contrib.auth.models import User
from .picture_saver import meme_json_parser

from .config import Secrets, Config

secrets = Secrets()
config = Config()


def get_random_picture(request):
    ip = log_in_user(request)
    mem = Meme.objects.exclude(profile__ip=ip).order_by("?").first()
    # mem = get_random_object_by_type(Meme)
    template = loader.get_template('void_app/feed.html')
    context = {
        'mem': mem,
        'server_url': config["main_server_url"]
    }
    return HttpResponse(template.render(context))


def get_random_object_by_type(object_type):
    return object_type.objects.order_by("?").first()


def add_like_to_meme(request, meme_id):
    Meme.objects.all().filter(id=meme_id).first().add_like()
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
        return ip
