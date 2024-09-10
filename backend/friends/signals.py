from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FriendRequest, Friendship
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from django.core.exceptions import ValidationError


# Helper function to send real-time notifications
def send_real_time_notification(user_id, message, notification_type):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'friend_requests_{user_id}',
        {
            'type': notification_type,
            'message': message
        }
    )


@receiver(post_save, sender=FriendRequest)
def friend_request_saved(sender, instance, created, **kwargs):
    if created:
        # Notify the receiver in real-time
        send_real_time_notification(
            instance.receiver.id,
            f"You have a new friend request from {instance.sender.username}.",
            'friend_request_notification'
        )
        print(f'FriendRequest created: {instance}')

        # Send email notification to the receiver
        try:
            send_mail(
                'New Friend Request',
                f'You have received a new friend request from {instance.sender.username}.',
                'from@example.com',
                [instance.receiver.email]
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

    if instance.status == 'accepted':
        # Automatically create a friendship if the friend request is accepted
        try:
            friendship, created = Friendship.objects.get_or_create(
                user1=min(instance.sender, instance.receiver, key=lambda u: u.id),
                user2=max(instance.sender, instance.receiver, key=lambda u: u.id),
            )
            if created:
                print(f'Friendship created automatically after friend request'
                      f' acceptance: {friendship}')
        except ValidationError as e:
            print(f'Error creating friendship: {e}')


@receiver(post_delete, sender=FriendRequest)
def friend_request_deleted(sender, instance, **kwargs):
    # Notify both the sender and receiver in real-time that the friend request was deleted
    send_real_time_notification(
        instance.receiver.id,
        f"Friend request from {instance.sender.username} has been deleted.",
        'friend_request_notification'
    )
    send_real_time_notification(
        instance.sender.id,
        f"Your friend request to {instance.receiver.username} has been deleted.",
        'friend_request_notification'
    )
    print(f'FriendRequest deleted: {instance}')


@receiver(post_save, sender=Friendship)
def friendship_saved(sender, instance, created, **kwargs):
    if created:
        # Notify both users in real-time that the friendship was created
        send_real_time_notification(
            instance.user1.id,
            f"You are now friends with {instance.user2.username}.",
            'friendship_notification'
        )
        send_real_time_notification(
            instance.user2.id,
            f"You are now friends with {instance.user1.username}.",
            'friendship_notification'
        )
        print(f'Friendship created: {instance}')


@receiver(post_delete, sender=Friendship)
def friendship_deleted(sender, instance, **kwargs):
    # Notify both users in real-time that the friendship was deleted
    send_real_time_notification(
        instance.user1.id,
        f"Your friendship with {instance.user2.username} has been removed.",
        'friendship_notification'
    )
    send_real_time_notification(
        instance.user2.id,
        f"Your friendship with {instance.user1.username} has been removed.",
        'friendship_notification'
    )
    print(f'Friendship deleted: {instance}')
