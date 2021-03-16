from django.contrib import admin

# Register your models here.
from potok_recommender.models import Ticket, Issuer

admin.site.register(Issuer)
admin.site.register(Ticket)
