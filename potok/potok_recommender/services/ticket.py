from potok_recommender.models import Ticket


def update_ticket(user_profile, ticket_json):
    ticket_id = ticket_json["id"]
    ticket_query = Ticket.objects.filter(id=ticket_id, profile=user_profile)
    if ticket_query.exists():
        ticket = ticket_query.first()
        ticket.id = ticket_json["id"]
        ticket.is_issued = ticket_json["is_issued"]
        ticket.is_returned = ticket_json["is_returned"]
        ticket.is_viewed = ticket_json["is_viewed"]
        ticket.is_liked = ticket_json["is_liked"]
        ticket.is_shared = ticket_json["is_shared"]
        ticket.save()
