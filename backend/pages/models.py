from mongoengine import Document, StringField, IntField, DateTimeField
from datetime import datetime

from core.models.base_models import MongoBaseModel


class Page(MongoBaseModel):
    """
    Page model to store user-created pages.
    Uses MongoDB through MongoEngine for flexible and scalable content storage.
    """
    user_id = IntField(required=True, help_text="ID of the user who created the page")
    user_username = StringField(max_length=150, required=True, help_text="Username of the user who created the page")
    title = StringField(max_length=255, required=True, help_text="Title of the page")
    content = StringField(help_text="Content of the page")

    meta = {
        'db_alias': 'social_db',
        'collection': 'pages',  # Collection name in MongoDB
        'ordering': ['-created_at'],  # Ordering pages by most recent
        'indexes': [
            'user_id',  # Index for efficient querying by user_id
            'title',    # Index for efficient querying by title
        ],
    }

    def __str__(self):
        return self.title
