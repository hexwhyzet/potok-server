from django.shortcuts import render
from .models import Meme
from django.http import HttpResponse


def get_random_picture(request):
    return HttpResponse(Meme.objects.get(id=1).meme_picture)
