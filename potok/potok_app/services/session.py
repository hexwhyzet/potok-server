from potok.potok_app.functions import id_gen
from potok.potok_app.models import Session


def session_by_token(token):
    return Session.objects.get(token=token)


def create_session(profile):
    for session in Session.objects.filter(profile=profile, is_opened=True):
        session.is_opened = False
        session.save()
    session = Session.objects.create(profile=profile, is_opened=True, token=id_gen(20))
    return session
