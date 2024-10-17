from mongoengine import Document, StringField, UUIDField, ListField, IntField, DateTimeField
from datetime import datetime
import uuid


class MongoBaseModel(Document):
    """
    Base model for MongoDB collections to include shared fields.
    """
    created_at = DateTimeField(default=datetime.utcnow, help_text="Timestamp of when the document was created")
    updated_at = DateTimeField(default=datetime.utcnow, help_text="Timestamp of when the document was last updated")

    meta = {
        'abstract': True
    }

    def save(self, *args, **kwargs):
        """
        Override the save method to update `updated_at` every time the document is saved.
        """
        if self.pk:  # If the document already exists, update `updated_at`
            self.updated_at = datetime.utcnow()
        return super(MongoBaseModel, self).save(*args, **kwargs)


class Comment(MongoBaseModel):
    """
    Represents a comment made by a user on a post.
    Stored in MongoDB as a document.
    """
    comment_id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4, required=True)
    user_id = IntField(required=True)
    user_username = StringField(max_length=150, required=True)
    post_id = UUIDField(binary=False, null=True, required=False)
    post_title = StringField(max_length=255, null=True, required=False)
    content = StringField(default='No content')
    tags = ListField(StringField(), default=list, blank=True)

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
