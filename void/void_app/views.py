from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader

from .models import Meme
from .picture_saver import meme_json_parser


def get_random_picture(request):
    mem = get_random_object_by_type(Meme)
    template = loader.get_template('void_app/feed.html')
    context = {
        'mem': mem,
    }
    return HttpResponse(template.render(context))


def get_random_object_by_type(object_type):
    return object_type.objects.order_by("?").first


def add_like_to_meme(request, meme_id):
    Meme.objects.all().filter(id=meme_id).first().add_like()
    return JsonResponse({'status': 'ok'})


def update_memes_db(request, post_json_info):
    with open('lellol.txt', 'w') as outfile:
        print(str(post_json_info), file=outfile)
    meme_json_parser(post_json_info)
    return JsonResponse({'status': 'ok'})