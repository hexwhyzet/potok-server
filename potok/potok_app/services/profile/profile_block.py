from potok_app.models import Profile, ProfileBlock


def does_block_exist(blocker: Profile, blocked: Profile):
    return ProfileBlock.objects.filter(blocker=blocker, blocked=blocked).exists()


def create_block(blocker: Profile, blocked: Profile):
    return ProfileBlock.objects.create(blocker=blocker, blocked=blocked)


def delete_block(blocker: Profile, blocked: Profile):
    return ProfileBlock.objects.get(blocker=blocker, blocked=blocked).delete()
