from potok_app.models import Profile, Subscription


def does_subscription_exist(follower: Profile, leader: Profile):
    return Subscription.objects.filter(follower=follower, leader=leader, accepted=True).exists()


def create_subscription(follower: Profile, leader: Profile):
    return Subscription.objects.create(follower=follower, leader=leader, accepted=leader.is_public)


def accept_subscription(follower: Profile, leader: Profile):
    subscription = Subscription.objects.get(follower=follower, leader=leader)
    subscription.is_accepted = True
    subscription.save()
    return subscription


def delete_subscription(follower: Profile, leader: Profile):
    return Subscription.objects.get(follower=follower, leader=leader).delete()
