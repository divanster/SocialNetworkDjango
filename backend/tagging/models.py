from django.db import models

# Create your models here.
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


class TaggedItem(models.Model):
    """
    Stores a tag of a user on any model instance.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    tagged_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_received',
        help_text='The user who is tagged.'
    )
    tagged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags_made',
        help_text='The user who tagged another user.'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'tagged_user')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tagged_by} tagged {self.tagged_user} on {self.content_object}"
