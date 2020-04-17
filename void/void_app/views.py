from django.shortcuts import render
from .models import Meme
from django.http import HttpResponse


def get_random_picture(request):
    pic = Meme.objects.get(id=1)
    html = "<html><body>It is now %s.</body></html>" % pic.meme_picture
    return HttpResponse(html)
