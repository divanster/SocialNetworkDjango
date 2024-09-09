from django.db import models
from core.models.base_models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        # Add other types as needed
    )
    sender = models.ForeignKey(User, related_name='sent_notifications',
                               on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_notifications',
                                 on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES,
                                         default='like')
    text = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} sent a {self.notification_type} notification to {self.receiver}"
