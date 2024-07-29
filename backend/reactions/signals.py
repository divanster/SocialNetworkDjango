# backend/reactions/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reaction


@receiver(post_save, sender=Reaction)
def reaction_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Reaction created: {instance}')
    else:
        print(f'Reaction updated: {instance}')


@receiver(post_delete, sender=Reaction)
def reaction_deleted(sender, instance, **kwargs):
    print(f'Reaction deleted: {instance}')
