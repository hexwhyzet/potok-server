from itertools import chain

from potok_app.models import Profile, Picture, View, Like, Subscription, Comment, CommentLike


def add_view(profile: Profile, picture: Picture):
    if not View.objects.filter(picture=picture, profile=profile).exists():
        picture.profile.views_num += 1
        picture.profile.save()

        picture.views_num += 1
        picture.save()

        View.objects.create(picture=picture, profile=profile)


def does_exist_unseen_subscription_picture(profile: Profile):
    return Picture.objects.filter(profile__followers=profile).exclude(profiles_viewed=profile).exists()


def switch_like(profile: Profile, picture: Picture):
    if Like.objects.filter(picture=picture, profile=profile).exists():
        Like.objects.get(picture=picture, profile=profile).delete()
        picture.likes_num -= 1
        picture.save()

        pic_profile = Profile.objects.get(pk=picture.profile.pk)
        pic_profile.likes_num -= 1
        pic_profile.save()
    else:
        Like.objects.create(picture=picture, profile=profile)
        picture.likes_num += 1
        picture.save()

        pic_profile = Profile.objects.get(pk=picture.profile.pk)
        pic_profile.likes_num += 1
        pic_profile.save()


def switch_subscription(follower: Profile, source: Profile):
    if Subscription.objects.filter(follower=follower, source=source).exists():
        unsubscribe(follower, source)
    else:
        subscribe(follower, source)


def unsubscribe(follower: Profile, source: Profile):
    if Subscription.objects.filter(follower=follower, source=source).exists():
        follower.subs_num -= 1
        follower.save()

        source.followers_num -= 1
        source.save()

        Subscription.objects.get(follower=follower, source=source).delete()


def subscribe(follower: Profile, source: Profile):
    if not Subscription.objects.filter(follower=follower, source=source).exists():
        follower.subs_num += 1
        follower.save()

        source.followers_num += 1
        source.save()

        Subscription.objects.create(follower=follower, source=source)


def last_actions(profile: Profile, number: int, offset: int):
    likes = Like.objects.filter(picture__profile=profile).order_by('-date')[offset:offset + number]
    subscriptions = Subscription.objects.filter(source=profile).order_by('-date')[offset:offset + number]
    actions = list(sorted(chain(likes, subscriptions), key=lambda action: action.date, reverse=True))[:number]
    return actions


def switch_like_comment(profile: Profile, comment: Comment):
    if not CommentLike.objects.filter(profile=profile, comment=comment).exists():
        CommentLike.objects.create(profile=profile, comment=comment)
        comment.likes_num += 1
        comment.save()
    else:
        CommentLike.objects.filter(profile=profile, comment=comment).delete()
        comment.likes_num -= 1
        comment.save()


def add_comment(profile: Profile, picture: Picture, text: str):
    Comment.objects.create(profile=profile, picture=picture, text=text)


def comment_can_be_deleted_by_user(user_profile: Profile, comment: Comment):
    return user_profile == comment.profile or comment.picture.profile == user_profile


def delete_comment(comment: Comment):
    comment.delete()


def comment_by_id(comment_id):
    return Comment.objects.get(id=comment_id)


def comments_of_picture(picture: Picture, number: int, offset: int):
    return Comment.objects.filter(picture=picture)[offset:offset + number]
