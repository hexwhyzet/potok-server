from ..models import Profile


def profile_by_id(profile_id):
    return Profile.objects.get(id=profile_id)
