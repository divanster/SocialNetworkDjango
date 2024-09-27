# backend/friends/tasks.py
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_friend_request(sender_username, receiver_email):
    try:
        send_mail(
            'New Friend Request',
            f'You have received a new friend request from {sender_username}.',
            'from@example.com',
            [receiver_email]
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
