from potok_app.models import Profile, ProfileAttachment


def available_attachments():
    return ProfileAttachment.objects.all()


def update_or_create_profile_attachment(profile: Profile, tag: ProfileAttachment.Tag, url: str):
    return ProfileAttachment.objects.update_or_create(profile=profile, tag=tag, defaults={'url': url})
