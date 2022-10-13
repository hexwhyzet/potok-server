from django.db import models

from potok_app.api.http_methods import DELETE, PUT
from potok_app.services.like.like import does_like_exist, delete_like, create_like


def like_content_object(request, content_object: models.Model):
    picture = content_object
    user_profile = request.user.profile

    if does_like_exist(picture, user_profile):
        if request.method == DELETE:
            delete_like(picture, user_profile)
    else:
        if request.method == PUT:
            create_like(picture, user_profile)
