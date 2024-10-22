from mongoengine import Document, StringField, UUIDField, ListField, IntField, \
    ReferenceField, DateTimeField, FileField
from core.models.base_models import MongoBaseModel, MongoUUIDModel, MongoSoftDeleteModel
from datetime import datetime
import uuid
import os
from bson import BSON
from gridfs import GridFS
from pymongo import MongoClient
from math import ceil
from django.conf import settings


# Helper function for generating file paths for album images
def album_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    # Sanitize title and generate a safe path
    sanitized_title = "".join(c if c.isalnum() else "_" for c in instance.title)
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(f'uploads/albums/{sanitized_title}/', filename)


# Initialize GridFS using settings variables
db_client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)  # Read from settings
db = db_client[settings.MONGO_DB_NAME]  # Replace 'mydatabase' with a setting
fs = GridFS(db)


class Photo(Document):
    """
    Represents a photo within an album.
    Stored as a separate document and referenced by the Album.
    """
    photo_id = UUIDField(binary=False, default=uuid.uuid4, required=True)
    album = ReferenceField('Album', reverse_delete_rule=2)  # Reference to Album
    image = FileField(required=True, help_text="GridFS reference to the image file")
    description = StringField(default="", required=False)
    tags = ListField(StringField(), default=list)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'photos',
        'indexes': ['album', 'created_at'],
    }

    def __str__(self):
        return f"Photo in album {self.album.title if self.album else 'Unknown'}"

    def save_image(self, image_path):
        """
        Save the image file to GridFS and store the reference.
        """
        try:
            with open(image_path, "rb") as f:
                file_id = fs.put(f, filename=os.path.basename(image_path))
            self.image = file_id
            self.save()
        except Exception as e:
            raise IOError(f"Failed to save image to GridFS: {e}")

    def get_image(self):
        """
        Retrieve the image file from GridFS.
        """
        try:
            return fs.get(self.image)
        except Exception as e:
            raise IOError(f"Failed to retrieve image from GridFS: {e}")


class Album(MongoUUIDModel, MongoSoftDeleteModel, MongoBaseModel):
    """
    Represents an album with related photos. Utilizes MongoDB through MongoEngine for
    storing nested data and improving performance.
    """
    user_id = IntField(required=True)
    user_username = StringField(max_length=150, required=True)
    title = StringField(max_length=255, required=True, unique_with="user_id")
    description = StringField(default="", required=False)
    tags = ListField(StringField(), default=list)  # Store tags as a list of strings

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

    def add_photo(self, image_path, description='', tags=None):
        """
        Method to add a photo to the album. Uses reference instead of embedding and
        stores the image in GridFS.
        """
        if tags is None:
            tags = []
        photo = Photo(album=self, description=description, tags=tags)

        # Estimate document size before attempting to save image to GridFS
        estimated_doc_size = BSON.encode(self.to_mongo()).__len__() + os.path.getsize(
            image_path)
        if estimated_doc_size >= 15 * 1024 * 1024:  # Check against 15MB (to leave
            # some margin)
            raise ValueError(
                "Adding this photo will exceed the BSON document size limit.")

        # Save image to GridFS
        photo.save_image(image_path)
        photo.save()

    @classmethod
    def active_albums(cls):
        """
        Method to retrieve only active (non-deleted) albums.
        """
        return cls.objects(is_deleted=False)

    def get_photos(self):
        """
        Retrieve all photos related to this album.
        """
        return Photo.objects(album=self)


# Pagination utility to return a chunk of data
def paginate_queryset(queryset, page_size=100):
    total_items = queryset.count()
    total_pages = ceil(total_items / page_size)
    for page in range(total_pages):
        yield queryset.skip(page * page_size).limit(page_size)


# Example method to get paginated photos
def get_paginated_photos(album_id, page_size=100):
    photos = Photo.objects(album=album_id)
    return paginate_queryset(photos, page_size)
