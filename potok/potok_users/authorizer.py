def get_user_profile(func):
    def wrapper(request, *args, **kwargs):
        return func(request, request.user.profile, *args, **kwargs)

    return wrapper
