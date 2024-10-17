from mongoengine import Document, StringField, UUIDField, ListField, IntField, DateTimeField
from datetime import datetime
import uuid
from core.models.base_models import MongoBaseModel  # Assuming the base model is in core.models.base_models


class Comment(MongoBaseModel):
    """
    Represents a comment made by a user on a post.
    Stored in MongoDB as a document.
    """
    comment_id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4, required=True)
    user_id = IntField(required=True, help_text="ID of the user who made the comment")
    user_username = StringField(max_length=150, required=True, help_text="Username of the user who made the comment")
    post_id = UUIDField(binary=False, null=True, required=False, help_text="ID of the related post")
    post_title = StringField(max_length=255, null=True, required=False, help_text="Title of the related post")
    content = StringField(default='No content', help_text="Content of the comment")
    tags = ListField(StringField(), default=list, help_text="List of tags associated with the comment")

    meta = {
        'collection': 'comments',  # MongoDB collection name
        'ordering': ['-created_at'],  # Ordering comments by most recent
        'indexes': [
            'user_id',
            'post_id',
            'created_at'
        ],
    }

    def __str__(self):
        return self.content[:20]

    def save(self, *args, **kwargs):
        """
        Override save method to update 'updated_at' timestamp on every update.
        """
        if self.pk:
            self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
