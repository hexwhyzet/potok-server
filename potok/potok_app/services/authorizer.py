from random import randint

from ..functions import id_gen
from ..models import CustomAnonymousUser, Profile, CustomUser


def get_device_id(request):
    if request.method == "GET":
        return request.GET["device_id"]
    elif request.method == "POST":
        return request.POST["device_id"]
    else:
        raise ValueError("Request has no attribute 'device_id'")


def get_token(request):
    if request.method == "GET":
        return request.GET["auth_token"]
    elif request.method == "POST":
        return request.POST["auth_token"]
    else:
        return ValueError("Request has no attribute 'token'")


def profile_by_token(request) -> Profile:
    token = get_token(request)
    if CustomAnonymousUser.objects.filter(token=token).exists():
        anonymous_user = CustomAnonymousUser.objects.filter(token=token).first()
        return anonymous_user.profile
    elif CustomUser.objects.filter(token=token).exists():
        user = CustomUser.objects.filter(token=token).first()
        return user.profile
    else:
        raise ValueError("User with this token was not found")


def login_user(func):
    def wrapper(request, *args, **kwargs):
        profile = profile_by_token(request)
        return func(request, profile, *args, **kwargs)

    return wrapper


def create_anonymous_user(device_id):
    random_int = randint(1, 1000000000)
    anonymous_user = CustomAnonymousUser(
        id=str(random_int),
        device_id=device_id,
        token=id_gen(80),
        username=random_int,
    )
    profile = Profile(
        user=anonymous_user,
    )
    anonymous_user.save()
    profile.save()
    return anonymous_user


def anonymous_user_by_device_id(device_id):
    return CustomAnonymousUser.objects.get(device_id=device_id)


def anonymous_user_exist(device_id):
    return CustomAnonymousUser.objects.filter(device_id=device_id).exists()
