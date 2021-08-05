from potok_app.models import Profile, Like


def does_like_exist(content_object, profile: Profile):
    return Like.objects.filter(content_object=content_object, profile=profile).exists()


def get_like(content_object, profile: Profile):
    return Like.objects.get(content_object=content_object, profile=profile)


def delete_like(content_object, profile: Profile):
    return get_like(content_object, profile).delete()


def create_like(content_object, profile: Profile):
    return Like.objects.create(content_object=content_object, profile=profile)
