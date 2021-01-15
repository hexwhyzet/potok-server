from potok_app.models import Picture, Profile, Session, Like


def picture_by_id(picture_id):
    return Picture.objects.get(id=picture_id)


def subscription_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.sub_pics.add(picture)
        session.save()
    return pictures


def feed_pictures(profile: Profile, session: Session, number: int):
    pictures = Picture.objects.exclude(profile__is_public=False).exclude(profiles_viewed=profile).exclude(
        id__in=[m.id for m in session.feed_pics.all() | session.sub_pics.all()]).exclude(
        profile__id=profile.id).order_by("-date")[:number]
    for picture in pictures:
        picture.views_num += 1
        picture.save()
        session.feed_pics.add(picture)
        session.save()
    return pictures


def profile_pictures(profile_id, number=10, offset=0):
    pictures = Picture.objects.filter(profile__id=profile_id).order_by('-date')[offset:offset + number]
    return pictures


def liked_pictures(profile_id, number=10, offset=0):
    pictures = list(
        map(lambda x: x.picture, Like.objects.filter(profile=profile_id).order_by('-date')[offset:offset + number]))
    return pictures
