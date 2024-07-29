# backend/follows/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow


@receiver(post_save, sender=Follow)
def follow_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Follow created: {instance}')


@receiver(post_delete, sender=Follow)
def follow_deleted(sender, instance, **kwargs):
    print(f'Follow deleted: {instance}')
