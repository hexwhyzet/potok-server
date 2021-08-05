from potok_users.models import User


def available_users():
    return User.objects.all()


def create_anonymous_user():
    return User.objects.create_anonymous_user()
