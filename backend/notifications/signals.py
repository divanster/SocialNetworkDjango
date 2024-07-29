# backend/notifications/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Notification created: {instance}')
    else:
        print(f'Notification updated: {instance}')


@receiver(post_delete, sender=Notification)
def notification_deleted(sender, instance, **kwargs):
    print(f'Notification deleted: {instance}')
