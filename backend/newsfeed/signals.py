import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums import album_models
from stories.models import Story
from .tasks import send_newsfeed_event_task

logger = logging.getLogger(__name__)


# Handlers for different models that are part of the newsfeed

@receiver(post_save, sender=Post)
def handle_post_save(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process post save event
    send_newsfeed_event_task.delay(instance.id, event_type, 'Post')
    logger.info(
        f"Triggered Celery task for post {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=Post)
def handle_post_delete(sender, instance, **kwargs):
    # Trigger Celery task to process post delete event
    send_newsfeed_event_task.delay(instance.id, 'deleted', 'Post')
    logger.info(f"Triggered Celery task for post deleted event with ID {instance.id}")


# Repeat similar signal handlers for Comment, Reaction, Album, and Story models

@receiver(post_save, sender=Comment)
def handle_comment_save(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process comment save event
    send_newsfeed_event_task.delay(instance.id, event_type, 'Comment')
    logger.info(
        f"Triggered Celery task for comment {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=Comment)
def handle_comment_delete(sender, instance, **kwargs):
    # Trigger Celery task to process comment delete event
    send_newsfeed_event_task.delay(instance.id, 'deleted', 'Comment')
    logger.info(
        f"Triggered Celery task for comment deleted event with ID {instance.id}")


@receiver(post_save, sender=Reaction)
def handle_reaction_save(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process reaction save event
    send_newsfeed_event_task.delay(instance.id, event_type, 'Reaction')
    logger.info(
        f"Triggered Celery task for reaction {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=Reaction)
def handle_reaction_delete(sender, instance, **kwargs):
    # Trigger Celery task to process reaction delete event
    send_newsfeed_event_task.delay(instance.id, 'deleted', 'Reaction')
    logger.info(
        f"Triggered Celery task for reaction deleted event with ID {instance.id}")


@receiver(post_save, sender=album_models)
def handle_album_save(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process album save event
    send_newsfeed_event_task.delay(instance.id, event_type, 'Album')
    logger.info(
        f"Triggered Celery task for album {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=album_models)
def handle_album_delete(sender, instance, **kwargs):
    # Trigger Celery task to process album delete event
    send_newsfeed_event_task.delay(instance.id, 'deleted', 'Album')
    logger.info(f"Triggered Celery task for album deleted event with ID {instance.id}")


@receiver(post_save, sender=Story)
def handle_story_save(sender, instance, created, **kwargs):
    event_type = 'created' if created else 'updated'
    # Trigger Celery task to process story save event
    send_newsfeed_event_task.delay(instance.id, event_type, 'Story')
    logger.info(
        f"Triggered Celery task for story {event_type} event with ID {instance.id}")


@receiver(post_delete, sender=Story)
def handle_story_delete(sender, instance, **kwargs):
    # Trigger Celery task to process story delete event
    send_newsfeed_event_task.delay(instance.id, 'deleted', 'Story')
    logger.info(f"Triggered Celery task for story deleted event with ID {instance.id}")
