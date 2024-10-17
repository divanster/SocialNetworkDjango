from mongoengine import Document, StringField, UUIDField, ListField, IntField, \
    ImageField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField
from datetime import datetime
import uuid
import os


def album_image_file_path(instance, filename):
    """
    Generate a unique file path for each uploaded image.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/albums/', filename)


class Photo(EmbeddedDocument):
    """
    Represents a photo within an album.
    Stored as an embedded document within the Album.
    """
    photo_id = UUIDField(binary=False, default=uuid.uuid4, required=True)
    album_title = StringField(max_length=255)
    image = ImageField(upload_to=album_image_file_path)
    description = StringField(blank=True)
    tags = ListField(StringField(), default=list)

    def __str__(self):
        return f"Photo in {self.album_title}"


class Album(Document):
    """
    Represents an album with related photos.
    """
    album_id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4,
                         required=True)
    user_id = IntField(required=True)
    user_username = StringField(max_length=150, required=True)
    title = StringField(max_length=255, required=True)
    description = StringField(blank=True)
    tags = ListField(StringField(), default=list)  # Store tags as a list of strings
    photos = ListField(EmbeddedDocumentField(Photo),
                       default=list)  # List of embedded Photo documents
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

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

    def save(self, *args, **kwargs):
        """
        Override save method to update 'updated_at' timestamp on every update.
        """
        if self.pk:
            self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def add_photo(self, album_title, image, description='', tags=None):
        """
        Method to add a photo to the album.
        """
        if tags is None:
            tags = []
        photo = Photo(album_title=album_title, image=image, description=description,
                      tags=tags)
        self.photos.append(photo)
        self.save()
