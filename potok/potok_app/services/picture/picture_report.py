from potok_app.models import Profile, Picture, PictureReport


def create_picture_report(picture: Picture, profile: Profile):
    return PictureReport.objects.update_or_create(picture=picture, profile=profile)
