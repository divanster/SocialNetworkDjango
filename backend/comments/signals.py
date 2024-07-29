# backend/comments/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment


@receiver(post_save, sender=Comment)
def comment_saved(sender, instance, created, **kwargs):
    if created:
        print(f'Comment created: {instance}')
    else:
        print(f'Comment updated: {instance}')


@receiver(post_delete, sender=Comment)
def comment_deleted(sender, instance, **kwargs):
    print(f'Comment deleted: {instance}')
