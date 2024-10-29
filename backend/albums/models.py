# albums/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation
from tagging.models import TaggedItem
import uuid
import os

User = get_user_model()


def album_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/album/', filename)


class Album(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Represents an album with related photos.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='albums',
        help_text="User who owns the album"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = GenericRelation(TaggedItem, related_query_name='albums')

    class Meta:
        db_table = 'albums'
        ordering = ['-created_at']
        unique_together = ('user', 'title')

    def __str__(self):
        return self.title

    def get_photos(self):
        """
        Retrieve all photos related to this album.
        """
        return self.photos.all()


class Photo(UUIDModel, BaseModel):
    """
    Represents a photo within an album.
    """
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)
    tags = GenericRelation(TaggedItem, related_query_name='photos')

    class Meta:
        db_table = 'photos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Photo in album '{self.album.title}'"

    def get_image_url(self):
        """
        Retrieve the URL of the image file.
        """
        if self.image:
            return self.image.url
        return None
