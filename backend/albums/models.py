from django.db import models
import uuid
import os
from django.utils import timezone
from core.models.base_models import BaseModel, SoftDeleteModel, UUIDModel

# Helper function for generating file paths for album images
def album_image_file_path(filename):
    """
    Generate a file path for the album image.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/album/', filename)


class Album(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Represents an album with related photos. Utilizes PostgreSQL for
    storing related data for better consistency and relational integrity.
    """
    user_id = models.IntegerField()  # Refers to the ID of the user who owns the album
    user_username = models.CharField(max_length=150)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)  # Store tags as a list of strings

    class Meta:
        db_table = 'albums'  # PostgreSQL table name
        ordering = ['-created_at']  # Ordering albums by most recent
        unique_together = ('user_id', 'title')  # Ensure title uniqueness per user

    def __str__(self):
        return self.title

    def add_photo(self, image_path, description='', tags=None):
        """
        Method to add a photo to the album.
        """
        if tags is None:
            tags = []

        # Create a Photo instance and save it
        photo = Photo.objects.create(
            album=self,
            description=description,
            tags=tags,
        )
        # Save the image file
        photo.save_image(image_path)

    @classmethod
    def active_albums(cls):
        """
        Method to retrieve only active (non-deleted) albums.
        """
        return cls.objects.filter(is_deleted=False)

    def get_photos(self):
        """
        Retrieve all photos related to this album.
        """
        return self.photos.all()


class Photo(UUIDModel, BaseModel):
    """
    Represents a photo within an album.
    Stored as a separate model and linked via a ForeignKey to the Album.
    """
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)  # Store tags as a list of strings
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'photos'  # PostgreSQL table name
        ordering = ['-created_at']

    def __str__(self):
        return f"Photo in album {self.album.title if self.album else 'Unknown'}"

    def save_image(self, image_path):
        """
        Save the image file to the `image` field of the Photo model.
        """
        if os.path.getsize(image_path) > 10 * 1024 * 1024:  # Limit to 10MB for example
            raise ValueError("Image file size exceeds the maximum limit of 10MB.")
        try:
            with open(image_path, "rb") as f:
                self.image.save(os.path.basename(image_path), f)
            self.save()
        except Exception as e:
            raise IOError(f"Failed to save image: {e}")

    def get_image_url(self):
        """
        Retrieve the URL of the image file.
        """
        if self.image:
            return self.image.url
        return None
