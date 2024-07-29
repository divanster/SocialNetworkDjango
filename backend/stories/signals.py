# backend/stories/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Story


@receiver(post_save, sender=Story)
def story_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Story created: {instance}')
    else:
        print(f'Story updated: {instance}')


@receiver(post_delete, sender=Story)
def story_deleted(sender, instance, **kwargs):
    print(f'Story deleted: {instance}')
