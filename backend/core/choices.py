# core/choices.py

from django.db import models


class VisibilityChoices(models.TextChoices):
    PUBLIC = 'public', 'Public'
    FRIENDS = 'friends', 'Friends'
    PRIVATE = 'private', 'Private'
