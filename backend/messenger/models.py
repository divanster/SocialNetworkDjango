# messenger/models.py

from django.db import models


class Message(models.Model):
    sender_id = models.IntegerField()
    sender_username = models.CharField(max_length=150)
    receiver_id = models.IntegerField(null=True, blank=True)
    receiver_username = models.CharField(max_length=150, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender_username} -> {self.receiver_username}: {self.content[:20]}"
