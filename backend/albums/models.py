from mongoengine import Document, StringField, UUIDField, ListField, IntField, \
    EmbeddedDocument, EmbeddedDocumentField, DateTimeField
from core.models.base_models import MongoBaseModel, MongoUUIDModel, MongoSoftDeleteModel
from datetime import datetime
import uuid
import os


# Helper function for generating file paths for album images
def album_image_file_path(instance, filename):
    """
    Generate a unique file path for each uploaded image.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/albums/', filename)


class Photo(MongoBaseModel, EmbeddedDocument):
    """
    Represents a photo within an album.
    Stored as an embedded document within the Album.
    """
    photo_id = UUIDField(binary=False, default=uuid.uuid4, required=True)
    album_title = StringField(max_length=255)
    image = StringField(required=True, help_text="Path to the image file")
    description = StringField(default="", required=False)
    tags = ListField(StringField(), default=list)

    def __str__(self):
        return f"Photo in {self.album_title}"


class Album(MongoUUIDModel, MongoSoftDeleteModel, MongoBaseModel):
    """
    Represents an album with related photos. Utilizes MongoDB through MongoEngine for
    storing nested data and improving performance.
    """
    user_id = IntField(required=True)
    user_username = StringField(max_length=150, required=True)
    title = StringField(max_length=255, required=True)
    description = StringField(default="", required=False)
    tags = ListField(StringField(), default=list)  # Store tags as a list of strings
    photos = ListField(EmbeddedDocumentField(Photo), default=list)  # List of
    # embedded Photo documents

    meta = {
        'collection': 'albums',  # MongoDB collection name
        'ordering': ['-created_at'],  # Ordering albums by most recent
        'indexes': [
            'user_id',
            'created_at'
        ],
    }

    def __str__(self):
        return self.title

    def add_photo(self, album_title, image, description='', tags=None):
        """
        Method to add a photo to the album.
        """
        if tags is None:
            tags = []
        photo = Photo(album_title=album_title, image=image, description=description, tags=tags)
        self.photos.append(photo)
        self.save()
