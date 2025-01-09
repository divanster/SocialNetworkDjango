# core/choices.py

from django.db import models


class VisibilityChoices(models.TextChoices):
    PUBLIC = 'public', 'Public'
    FRIENDS = 'friends', 'Friends'
    PRIVATE = 'private', 'Private'


class StoryEventTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    SOFT_DELETED = 'soft_deleted', 'Soft Deleted'
    RESTORED = 'restored', 'Restored'


class PostEventTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    DELETED = 'deleted', 'Deleted'
    SOFT_DELETED = 'soft_deleted', 'Soft Deleted'
    RESTORED = 'restored', 'Restored'


class UserEventTypes(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    SOFT_DELETED = 'soft_deleted', 'Soft Deleted'
    RESTORED = 'restored', 'Restored'
