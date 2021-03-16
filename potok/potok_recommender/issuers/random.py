from potok_app.models import Picture, Profile
from potok_recommender.models import Ticket, Issuer


def random_process_issue(profile: Profile, number):
    not_issued_tickets_num = Ticket.objects.filter(is_issued=False).count()
    if not_issued_tickets_num < 30:
        random_generate_tickets(profile, 30)

    return random_tickets(profile, number)


def random_generate_tickets(profile: Profile, number: int):
    issuer, _ = Issuer.objects.get_or_create(name="random")
    pictures = Picture.objects.exclude(profile__is_public=False).exclude(profiles_viewed=profile).exclude().exclude(
        profile__id=profile.id).exclude(profile__in=profile.blocked_profiles.all()).exclude(pk__in=[p.picture.pk for p in profile.tickets.all()]).order_by("-date")[:number]
    for picture in pictures:
        ticket = Ticket.objects.create(
            picture=picture,
            profile=profile,
            issuer=issuer,
        )
        ticket.token = f"random-{ticket.id}"
        ticket.save()


def random_tickets(profile: Profile, number: int):
    tickets = Ticket.objects.filter(is_issued=False, profile=profile).order_by("date_created")[:number]
    for ticket in tickets:
        ticket.is_issued = True
    Ticket.objects.bulk_update(tickets, ["is_issued"])
    return tickets
