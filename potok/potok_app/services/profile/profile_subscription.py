from django.db.models import signals
from django.dispatch import receiver

from potok_app.models import Profile, Subscription


def does_subscription_exist(follower: Profile, leader: Profile):
    return Subscription.objects.filter(follower=follower, leader=leader).exists()


def get_subscription(follower: Profile, leader: Profile):
    return Subscription.objects.get(follower=follower, leader=leader)


def does_subscription_exist_and_accepted(follower: Profile, leader: Profile):
    return does_subscription_exist(follower=follower, leader=leader).exists() \
           and get_subscription(follower=follower, leader=leader).is_accepted


def safe_create_subscription(follower: Profile, leader: Profile):
    Subscription.objects.get_or_create(follower=follower, leader=leader, is_accepted=(not leader.is_private))


def accept_subscription(follower: Profile, leader: Profile):
    subscription = Subscription.objects.get(follower=follower, leader=leader)
    subscription.is_accepted = True
    subscription.save()
    return subscription


def safe_delete_subscription(follower: Profile, leader: Profile):
    return Subscription.objects.filter(follower=follower, leader=leader).delete()


@receiver(signals.pre_delete, sender=Subscription)
def subscription_delete(sender, instance: Subscription, **kwargs):
    instance.follower.leaders_num -= 1
    instance.follower.save()
    instance.leader.followers_num -= 1
    instance.leader.save()


@receiver(signals.pre_save, sender=Subscription)
def subscription_save(sender, instance: Subscription, **kwargs):
    instance.follower.leaders_num += 1
    instance.follower.save()
    instance.leader.followers_num += 1
    instance.leader.save()
