# backend/messenger/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message


@receiver(post_save, sender=Message)
def message_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Message created: {instance}')


@receiver(post_delete, sender=Message)
def message_deleted(sender, instance, **kwargs):
    print(f'Message deleted: {instance}')
