# backend/core/utils.py

# Kafka producer utility
from kafka_app.producer import KafkaProducerClient
from django.contrib.auth import get_user_model
from friends.models import Friendship, User
from django.db import models

def get_kafka_producer():
    """
    Returns a shared instance of KafkaProducerClient for all apps.
    """
    return KafkaProducerClient()

def get_friends(user):
    """
    Retrieve the friends of the given user.

    Args:
        user (User): The user whose friends we want to retrieve.

    Returns:
        QuerySet: A QuerySet of users who are friends with the given user.
    """
    friends = Friendship.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    )
    friend_ids = set()
    for friendship in friends:
        friend_ids.add(friendship.user1_id)
        friend_ids.add(friendship.user2_id)
    friend_ids.discard(user.id)
    return User.objects.filter(id__in=friend_ids)
