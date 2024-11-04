import logging
from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel, SoftDeleteManager
from django.contrib.contenttypes.fields import GenericRelation
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Import visibility choices
import uuid
import os
from core.utils import get_friends

User = get_user_model()

logger = logging.getLogger(__name__)

def album_image_file_path(instance, filename):
    """
    Generate file path for new album image.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(f'uploads/album/{instance.album.user.id}/', filename)


class AlbumQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """
        Filter albums visible to the user based on visibility settings.
        """
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC, is_deleted=False)
        else:
            public_albums = self.filter(visibility=VisibilityChoices.PUBLIC, is_deleted=False)
            friends_albums = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                user__in=get_friends(user),
                is_deleted=False
            )
            own_albums = self.filter(user=user, is_deleted=False)
            return public_albums | friends_albums | own_albums


class AlbumManager(SoftDeleteManager):
    def get_queryset(self):
        """
        Override get_queryset to use AlbumQuerySet.
        """
        return AlbumQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def visible_to_user(self, user):
        """
        Return albums visible to the specified user.
        """
        return self.get_queryset().visible_to_user(user)


class Album(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Represents an album with related photos and visibility settings.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='albums',
        help_text="User who owns the album"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        help_text="Visibility of the album"
    )
    tags = GenericRelation(TaggedItem, related_query_name='albums')

    objects = AlbumManager()  # Use custom manager

    class Meta:
        db_table = 'albums'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_user_album_title')
        ]
        indexes = [
            models.Index(fields=['user'], name='user_idx'),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return self.title

    def get_photos(self):
        """
        Retrieve all photos related to this album.
        """
        try:
            return self.photos.filter(is_deleted=False)
        except Exception as e:
            logger.error(f"Error retrieving photos for album {self.id}: {e}")
            return []


class PhotoQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """
        Filter photos visible to the user based on the visibility of the album.
        """
        if user.is_anonymous:
            return self.filter(album__visibility=VisibilityChoices.PUBLIC, album__is_deleted=False, is_deleted=False)
        else:
            public_photos = self.filter(album__visibility=VisibilityChoices.PUBLIC, album__is_deleted=False, is_deleted=False)
            friends_photos = self.filter(
                album__visibility=VisibilityChoices.FRIENDS,
                album__user__in=get_friends(user),
                album__is_deleted=False,
                is_deleted=False
            )
            own_photos = self.filter(album__user=user, album__is_deleted=False, is_deleted=False)
            return public_photos | friends_photos | own_photos


class PhotoManager(SoftDeleteManager):
    def get_queryset(self):
        """
        Override get_queryset to use PhotoQuerySet.
        """
        return PhotoQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def visible_to_user(self, user):
        """
        Return photos visible to the specified user.
        """
        return self.get_queryset().visible_to_user(user)


class Photo(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Represents a photo within an album with visibility settings derived from the album.
    """
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        help_text="Album to which this photo belongs"
    )
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)
    tags = GenericRelation(TaggedItem, related_query_name='photos')

    objects = PhotoManager()  # Use custom manager

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
