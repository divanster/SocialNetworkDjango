# backend/users/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import CustomUser
from users.tasks import process_user_event_task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def handle_user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to trigger a Celery task for handling user events.
    """
    event_type = 'new_user' if created else 'profile_update'
    process_user_event_task.delay(instance.id, event_type)
    logger.info(f"Triggered Celery task for user {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=CustomUser)
def handle_user_post_delete(sender, instance, **kwargs):
    """
    Signal handler to trigger a Celery task for handling user deletion events.
    """
    process_user_event_task.delay(instance.id, 'deleted_user')
    logger.info(f"Triggered Celery task for deleted user with ID {instance.id}")
