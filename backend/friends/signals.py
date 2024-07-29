# backend/friends/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship


@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    if created:
        print(f'FriendRequest created: {instance}')


@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    print(f'FriendRequest deleted: {instance}')


@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Friendship created: {instance}')


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    print(f'Friendship deleted: {instance}')
