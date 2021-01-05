from itertools import chain

from potok_app.models import Profile, Picture, View, Like, Subscription, Comment, CommentLike


def add_view(profile: Profile, picture: Picture):
    View.objects.create(picture=picture, profile=profile)


def does_exist_unseen_subscription_picture(profile: Profile):
    return Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exists()


def switch_like(profile: Profile, picture: Picture):
    if Like.objects.filter(picture=picture, profile=profile).exists():
        Like.objects.get(picture=picture, profile=profile).delete()
        picture.likes_num -= max(0, picture.likes_num - 1)
    else:
        Like.objects.create(picture=picture, profile=profile)
        picture.likes_num += 1
    picture.save()


def switch_subscription(follower: Profile, source: Profile):
    if Subscription.objects.filter(follower=follower, source=source).exists():
        Subscription.objects.get(follower=follower, source=source).delete()
    else:
        Subscription.objects.create(follower=follower, source=source)


def last_actions(profile: Profile, number: int, offset: int):
    likes = Like.objects.filter(picture__profile=profile).order_by('-date')[:offset + number]
    subscriptions = Subscription.objects.filter(source=profile).order_by('-date')[:offset + number]
    actions = list(sorted(chain(likes, subscriptions), key=lambda action: action.date))[offset:offset + number]
    return actions


def like_comment(profile: Profile, comment: Comment):
    CommentLike.objects.create(profile=profile, comment=comment)


def add_comment(profile: Profile, picture: Picture, text: str):
    Comment.objects.create(author=profile, picture=picture, text=text)


def comment_by_id(comment_id):
    return Comment.objects.get(id=comment_id)
