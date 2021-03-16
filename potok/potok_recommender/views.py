from json import loads
from typing import List

from django.views.decorators.csrf import csrf_exempt

from potok_app.models import Profile
from potok_app.services.authorizer import login_user
from potok_app.services.profile import profile_by_id
from potok_app.views import construct_app_response, construct_picture_response, construct_profile_response
from potok_recommender.models import Ticket
from potok_recommender.services.issuer import get_issuer
from potok_recommender.services.ticket import update_ticket


def construct_ticket_response(ticket: Ticket, user_profile: Profile):
    response_content = {
        "type": "ticket",
        "id": ticket.id,
        "token": ticket.token,

        # "is_issued": ticket.is_issued,
        # "is_returned": ticket.is_returned,
        # "is_viewed": ticket.is_viewed,
        # "is_liked": ticket.is_liked,
        # "is_shared": ticket.is_shared,

        "picture": construct_picture_response(ticket.picture, user_profile),
        "profile": construct_profile_response(ticket.profile, user_profile),

        "date_created": int(ticket.date_created.timestamp()),
        # "date_realized": int(ticket.date_realized.timestamp()),
    }
    return response_content


def construct_tickets(tickets: List[Ticket], user_profile: Profile):
    return [construct_ticket_response(ticket, user_profile) for ticket in tickets]


def issue_tickets_by_profile_id(profile_id: int):
    profile = profile_by_id(profile_id)
    return issue_tickets_by_profile(profile=profile)


def issue_tickets_by_profile(profile: Profile, number):
    issuer_function = get_issuer(profile)
    tickets = issuer_function(profile, number)
    for ticket in tickets:
        ticket.is_issued = True
    Ticket.objects.bulk_update(tickets, ["is_issued"])
    return tickets


def refresh_issued_tickets(profile_id: int):
    profile = profile_by_id(profile_id)
    Ticket.objects.filter(profile=profile, is_viewed=False, is_issued=True).update(is_issued=False)


@login_user
def app_tickets(request, user_profile, number):
    tickets = issue_tickets_by_profile(user_profile, number)
    constructed_response = construct_tickets(tickets, user_profile)
    return construct_app_response("ok", constructed_response)


@csrf_exempt
@login_user
def app_return_tickets(request, user_profile):
    content = request.POST["content"]
    tickets = loads(content)
    for ticket in tickets:
        update_ticket(user_profile, ticket)
    return construct_app_response("ok", None)
