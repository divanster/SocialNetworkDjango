# backend/pages/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Page


@receiver(post_save, sender=Page)
def page_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Page created: {instance}')
    else:
        print(f'Page updated: {instance}')


@receiver(post_delete, sender=Page)
def page_deleted(sender, instance, **kwargs):
    print(f'Page deleted: {instance}')
