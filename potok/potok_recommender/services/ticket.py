from potok_app.models import Profile
from potok_recommender.models import Ticket


def update_ticket(user_profile, ticket_json):
    ticket_id = ticket_json["id"]
    ticket_query = Ticket.objects.filter(id=ticket_id, profile=user_profile)
    if ticket_query.exists():
        ticket = ticket_query.first()
        ticket.id = ticket_json["id"]
        ticket.is_issued = ticket_json["is_issued"]
        ticket.is_returned = True
        ticket.is_viewed = ticket_json["is_viewed"]
        ticket.is_liked = ticket_json["is_liked"]
        ticket.is_shared = ticket_json["is_shared"]
        ticket.save()


def not_issued_tickets(profile: Profile):
    return Ticket.objects.filter(is_issued=False, profile=profile)


def return_tickets(user_profile, tickets):
    for ticket in tickets:
        update_ticket(user_profile, ticket)

    # ids = list(map(lambda x: x['id'], tickets))
    # latest_ticket_date_created = Ticket.objects.filter(id__in=ids).order_by('-date_created')[0].date_created
    #
    # Ticket.objects.filter(is_returned=False, date_created__lte=latest_ticket_date_created).update(is_issued=False)
