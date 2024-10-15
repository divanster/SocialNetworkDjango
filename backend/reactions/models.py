# reactions/models.py

from django.db import models


class Reaction(models.Model):
    EMOJI_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=150)
    reacted_item_type = models.CharField(
        max_length=100)  # E.g., 'Post', 'Comment', etc.
    reacted_item_id = models.CharField(
        max_length=255)  # Use CharField to accommodate various ID types
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'reacted_item_type', 'reacted_item_id', 'emoji')

    def __str__(self):
        return f"{self.user_username} reacted with {self.emoji} on {self.reacted_item_type} {self.reacted_item_id}"
