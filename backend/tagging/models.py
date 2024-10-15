# tagging/models.py

from django.db import models


class TaggedItem(models.Model):
    """
    Stores a tag of a user on any model instance.
    """
    tagged_item_type = models.CharField(max_length=100)
    tagged_item_id = models.CharField(max_length=255)
    tagged_user_id = models.IntegerField()
    tagged_user_username = models.CharField(max_length=150)
    tagged_by_id = models.IntegerField()
    tagged_by_username = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tagged_item_type', 'tagged_item_id', 'tagged_user_id')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tagged_by_username} tagged {self.tagged_user_username} on {self.tagged_item_type} {self.tagged_item_id}"
