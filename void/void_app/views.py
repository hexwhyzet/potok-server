from django.shortcuts import render
from .models import Meme
from django.http import HttpResponse
from django.template import loader
from random import randint


def get_random_picture(request):
    mem = Meme.objects.get(id=randint(3, 4))
    template = loader.get_template('void_app/feed.html')
    context = {
        'mem': mem,
    }
    return HttpResponse(template.render(context))
