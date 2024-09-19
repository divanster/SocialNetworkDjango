from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TaggedItem
from notifications.models import Notification


@receiver(post_save, sender=TaggedItem)
def notify_tagged_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.tagged_user,
            actor=instance.tagged_by,
            verb='tagged you',
            target=instance.content_object
        )
