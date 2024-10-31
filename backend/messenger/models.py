from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel

User = get_user_model()

class Message(UUIDModel, BaseModel):
    """
    Stores messages sent between users using PostgreSQL.
    """
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        help_text="User who sent the message"
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE,
        help_text="User who received the message"
    )
    content = models.TextField(help_text="Content of the message")
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the message has been read"
    )

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'is_read']),
        ]

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:20]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
