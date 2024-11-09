from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel

User = get_user_model()


class Conversation(UUIDModel, BaseModel):
    """
    Represents a conversation between multiple users.
    """
    participants = models.ManyToManyField(User, related_name='conversations')

    def __str__(self):
        participants_list = [participant.username for participant in self.participants.all()]
        return f"Conversation between {', '.join(participants_list)}"

    def add_participant(self, user):
        if user not in self.participants.all():
            self.participants.add(user)

    def remove_participant(self, user):
        if user in self.participants.all():
            self.participants.remove(user)


class Message(UUIDModel, BaseModel):
    """
    Stores messages sent between users using PostgreSQL.
    """
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE,
        help_text="Conversation to which this message belongs",
        null=False
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        help_text="User who sent the message"
    )
    content = models.TextField(help_text="Content of the message")
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the message has been read"
    )
    deleted_by_sender = models.BooleanField(default=False, help_text="Indicates if sender deleted the message")
    deleted_by_receiver = models.BooleanField(default=False, help_text="Indicates if receiver deleted the message")

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"From {self.sender.username}: {self.content[:20]}"

    def mark_as_read(self):
        """
        Marks the message as read.
        """
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_as_deleted(self, user):
        """
        Soft deletes the message for the given user.
        """
        if user == self.sender:
            self.deleted_by_sender = True
        elif user in self.conversation.participants.exclude(pk=self.sender.pk):
            self.deleted_by_receiver = True
        self.save(update_fields=['deleted_by_sender', 'deleted_by_receiver'])

    def is_visible_to(self, user):
        """
        Checks if the message is visible to the given user.
        """
        if user == self.sender and not self.deleted_by_sender:
            return True
        if user in self.conversation.participants.exclude(pk=self.sender.pk) and not self.deleted_by_receiver:
            return True
        return False
