from django.contrib import admin

from potok_users.models import User, AccountVerificationCode

admin.site.register(User)
admin.site.register(AccountVerificationCode)
