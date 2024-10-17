from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField
from datetime import datetime

# Defining notification types as a choice field
NOTIFICATION_TYPES = (
    ('like', 'Like'),
    ('comment', 'Comment'),
    ('follow', 'Follow'),
    ('tag', 'Tag'),
    ('friend_request', 'Friend Request'),
    ('message', 'Message'),
    ('reaction', 'Reaction'),
    ('accepted_request', 'Accepted Friend Request'),
    ('post', 'New Post'),
    ('update', 'Profile Update'),
    # Add more as needed
)

class Notification(Document):
    """
    Notification model for storing notification events.
    Uses MongoDB through MongoEngine to handle high volume and flexible data efficiently.
    """
    sender_id = IntField(required=True, help_text="ID of the user sending the notification")
    sender_username = StringField(max_length=150, required=True, help_text="Username of the sender")
    receiver_id = IntField(required=True, help_text="ID of the user receiving the notification")
    receiver_username = StringField(max_length=150, required=True, help_text="Username of the receiver")
    notification_type = StringField(
        max_length=21, choices=NOTIFICATION_TYPES, default='like', help_text="Type of notification"
    )
    text = StringField(blank=True, help_text="Additional text for the notification")
    is_read = BooleanField(default=False, help_text="Indicates whether the notification has been read")
    content_type = StringField(max_length=100, null=True, blank=True, help_text="Content type related to the notification")
    object_id = StringField(max_length=255, null=True, blank=True, help_text="Object ID related to the notification")
    created_at = DateTimeField(default=datetime.utcnow, help_text="Timestamp when the notification was created")

    meta = {
        'collection': 'notifications',
        'ordering': ['-created_at'],
        'indexes': [
            'receiver_id',  # Index for efficient querying by receiver
            ('sender_id', 'receiver_id'),  # Compound index for sender and receiver queries
        ],
    }

    def __str__(self):
        return (f"{self.sender_username} sent a {self.get_notification_type_display()} "
                f"notification to {self.receiver_username}")

    def get_notification_type_display(self):
        """
        Helper method to get the readable form of notification type.
        """
        return dict(NOTIFICATION_TYPES).get(self.notification_type, "Unknown")

    def mark_as_read(self):
        """
        Helper method to mark the notification as read.
        """
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_content_object_url(self):
        """
        Helper method to get the URL of the related content object if it exists.
        Constructs the URL based on `content_type` and `object_id`.
        """
        if self.content_type and self.object_id:
            # Construct a placeholder URL based on content_type and object_id
            return f"/{self.content_type.lower()}/{self.object_id}/"
        return None
