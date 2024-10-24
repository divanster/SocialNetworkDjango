# backend/albums/album_models.py

from mongoengine import StringField, UUIDField, ListField, IntField
from core.models.base_models import MongoUUIDModel, MongoSoftDeleteModel, MongoBaseModel
from bson import BSON
import os
from .photo_models import Photo  # Import the Photo model from the same directory

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
        estimated_doc_size = BSON.encode(self.to_mongo()).__len__() + os.path.getsize(image_path)
        if estimated_doc_size >= 15 * 1024 * 1024:  # Check against 15MB (to leave some margin)
            raise ValueError("Adding this photo will exceed the BSON document size limit.")

        # Save image to GridFS and save the photo document
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
