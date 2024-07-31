from django.db import models
from django.contrib.auth import get_user_model
from social.models import Post  # Adjust import as needed

User = get_user_model()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments',
                             null=True, blank=True)
    content = models.TextField(default='No content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20]
