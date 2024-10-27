from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField
from datetime import datetime

from core.models.base_models import MongoUUIDModel, MongoBaseModel, MongoSoftDeleteModel


class Message(MongoUUIDModel, MongoBaseModel, MongoSoftDeleteModel):
    """
    Stores the messages sent between users.
    Uses MongoDB through MongoEngine to leverage high performance in handling
    high-volume, document-based message data.
    """
    sender_id = IntField(required=True, help_text="ID of the sender")
    sender_username = StringField(max_length=150, required=True,
                                  help_text="Username of the sender")
    receiver_id = IntField(null=True, blank=True, help_text="ID of the receiver")
    receiver_username = StringField(max_length=150, null=True, blank=True,
                                    help_text="Username of the receiver")
    content = StringField(required=True, help_text="Content of the message")
    timestamp = DateTimeField(default=datetime.utcnow,
                              help_text="Timestamp of when the message was sent")
    is_read = BooleanField(default=False,
                           help_text="Boolean indicating if the message was read")

    meta = {
        'db_alias': 'social_db',
        'collection': 'messages',
        'ordering': ['-timestamp'],
        'indexes': [
            {'fields': ['sender_id', 'receiver_id']},
            {'fields': ['$content'], 'default_language': 'english'}
        ],
    }

    def __str__(self):
        return f"{self.sender_username} -> {self.receiver_username}: {self.content[:20]}"

    def mark_as_read(self):
        """
        Helper method to mark the message as read.
        """
        if not self.is_read:
            self.is_read = True
            self.save()
