from mongoengine import StringField, IntField, DateTimeField, ListField, URLField, \
    BooleanField
from core.models.base_models import MongoBaseModel  # Import MongoBaseModel from core
from datetime import datetime


class Story(MongoBaseModel):
    """
    A model representing a user's story.
    """
    user_id = IntField(required=True, min_value=1,
                       help_text="ID of the user who created the story")
    user_username = StringField(max_length=150, required=True,
                                help_text="Username of the user who created the story")

    # Fields for different types of story content
    content = StringField(
        help_text="Text content of the story. Keep it short and engaging.", null=True)
    media_type = StringField(choices=('image', 'video', 'text'),
                             help_text="Type of the story content", default="text")
    media_url = URLField(help_text="URL of the media for the story (if applicable)",
                         null=True)

    is_active = BooleanField(default=True,
                             help_text="Is the story active or has it expired?")
    viewed_by = ListField(IntField(),
                          help_text="List of user IDs who have viewed this story")

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

    def deactivate_story(self):
        """
        Mark the story as inactive after the expiration period.
        """
        self.is_active = False
        self.save()

    def has_expired(self):
        """
        Check if the story has expired based on a time limit.
        """
        expiration_time = datetime.now() - self.created_at
        return expiration_time.total_seconds() > 86400  # Example: 24 hours (24 * 60 * 60)

    def add_view(self, user_id):
        """
        Add a user to the list of those who have viewed the story.
        """
        if user_id not in self.viewed_by:
            self.viewed_by.append(user_id)
            self.save()
