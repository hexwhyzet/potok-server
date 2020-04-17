from django.shortcuts import render
from .models import Meme
from django.http import HttpResponse


def get_random_picture(request):
    with open(str(Meme.objects.get(id=3).meme_picture), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpg")
