from django.db import models

from potok_app.models import Picture, Profile


class Issuer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=200, null=False, blank=False, unique=True)

    is_issued = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, related_name='tickets', blank=True, null=True)

    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='tickets')

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tickets')

    date_created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    date_realized = models.DateTimeField(null=True, blank=True)
