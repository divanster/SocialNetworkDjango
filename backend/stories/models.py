from mongoengine import StringField, IntField
from core.models.base_models import MongoBaseModel  # Import MongoBaseModel from core
from datetime import datetime
from django.core.validators import MinValueValidator


class Story(MongoBaseModel):
    """
    A model representing a user's story.
    """
    user_id = IntField(required=True, min_value=1, help_text="ID of the user who "
                                                             "created the story")
    user_username = StringField(max_length=150, required=True, help_text="Username of "
                                                                         "the user "
                                                                         "who created "
                                                                         "the story")
    content = StringField(required=True, help_text="Content of the story. Keep it "
                                                   "short and engaging.")

    meta = {
        'collection': 'stories',  # MongoDB collection name
        'ordering': ['-created_at'],  # Ordering stories by most recent
        'indexes': [
            'user_id',
            'created_at'
        ],
    }

    def __str__(self):
        return f"Story by {self.user_username} at {self.created_at}"
