from django.contrib import admin
from .models import Profile

# Register your models here.
from .models import Meme

admin.site.register(Meme)
admin.site.register(Profile)
