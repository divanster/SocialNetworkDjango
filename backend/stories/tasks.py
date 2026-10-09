from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from stories.models import Story


@shared_task
def deactivate_expired_stories():
    cutoff = timezone.now() - timedelta(hours=24)
    return Story.objects.filter(
        is_active=True,
        is_deleted=False,
        created_at__lt=cutoff
    ).update(is_active=False)
