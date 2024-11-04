# backend/users/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import CustomUser, UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserProfile when a CustomUser is first created.
    """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if created:
            logger.info(f"UserProfile created for new user with ID {instance.id}")
        else:
            logger.info(f"UserProfile already existed for user with ID {instance.id}")


@receiver(post_delete, sender=CustomUser)
def delete_user_profile(sender, instance, **kwargs):
    """
    Signal to delete the UserProfile when a CustomUser instance is deleted.
    """
    try:
        if hasattr(instance, 'profile'):
            instance.profile.delete()
            logger.info(f"UserProfile deleted for user with ID {instance.id}")
    except UserProfile.DoesNotExist:
        logger.warning(
            f"Attempted to delete UserProfile for user ID {instance.id}, but it did not exist.")
