# albums/models.py

from django.db import models
from core.models.base_models import BaseModel, FilePathModel
import uuid
import os


def album_image_file_path(instance, filename):
    return instance.generate_file_path(filename)


class Album(BaseModel):
    album_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=150)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list,
                            blank=True)  # Store tags as a list of strings or IDs

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Photo(FilePathModel, BaseModel):
    album_id = models.UUIDField()
    album_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Photo in {self.album_title}"
