# backend/albums/photo_models.py

from mongoengine import Document, StringField, UUIDField, ListField, ReferenceField, DateTimeField, FileField
from core.utils import get_mongo_client  # Import the utility function for MongoDB connection
from django.conf import settings
from datetime import datetime
import uuid
import os
from gridfs import GridFS

# Initialize GridFS using the utility function
db_client = get_mongo_client()  # Utilize the utility function
db = db_client[settings.MONGO_DB_NAME]  # Get the database using Django settings
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
        if os.path.getsize(image_path) > 10 * 1024 * 1024:  # Limit to 10MB for example
            raise ValueError("Image file size exceeds the maximum limit of 10MB.")
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
