from potok_app.models import Profile
from potok_recommender.issuers.random import random_process_issue


def get_issuer(profile: Profile):
    return random_process_issue


def process_issue(issuer_function):
    return
