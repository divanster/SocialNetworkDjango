# backend/reactions/models.py
from django.db import models
from django.contrib.auth import get_user_model
from social.models import Post

User = get_user_model()


class Reaction(models.Model):
    EMOJI_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='reactions',
                             on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10, choices=EMOJI_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'emoji')

    def __str__(self):
        return f"{self.user.username} reacted with {self.emoji} to {self.post.title}"
