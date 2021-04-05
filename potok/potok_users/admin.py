from django.contrib import admin

from potok_users.models import User, VerificationCode

admin.site.register(User)
admin.site.register(VerificationCode)
