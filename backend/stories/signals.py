# backend/stories/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Story

# Initialize logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story)
def story_saved(sender, instance, created, **kwargs):
    """
    Signal to handle logic after a Story instance is saved.
    Logs whether the story was created or updated.
    """
    if created:
        logger.info(
            f'Story created with ID: {instance.id}, User: {instance.user_username}, Content: {instance.content[:30]}')
    else:
        logger.info(
            f'Story updated with ID: {instance.id}, User: {instance.user_username}, Content: {instance.content[:30]}')


@receiver(post_delete, sender=Story)
def story_deleted(sender, instance, **kwargs):
    """
    Signal to handle logic after a Story instance is deleted.
    Logs the deletion of the story.
    """
    logger.info(
        f'Story deleted with ID: {instance.id}, User: {instance.user_username}, Content: {instance.content[:30]}')
