from potok_app.models import Comment, Profile, Picture


def available_comments():
    return Comment.objects.all()


def comments_by_picture(picture: Picture):
    return Comment.objects.filter(picture=picture)


def comment_by_id(comment_id):
    return Comment.objects.get(id=comment_id)


def create_comment(picture: Picture, profile: Profile, text: str):
    new_comment = Comment.objects.create(profile=profile, picture=picture, text=text)
    new_comment.picture.comments_num += 1
    new_comment.picture.save()
    return new_comment


def delete_comment(comment: Comment, text: str):
    picture = comment.picture
    comment.delete()
    picture.comments_num -= 1
    picture.save()
