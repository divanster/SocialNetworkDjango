# backend/albums/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Album


@receiver(post_save, sender=Album)
def album_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Album created: {instance}')
    else:
        print(f'Album updated: {instance}')


@receiver(post_delete, sender=Album)
def album_deleted(sender, instance, **kwargs):
    print(f'Album deleted: {instance}')
