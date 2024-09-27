from django.db import models
from django.contrib.auth import get_user_model

from core.models.base_models import BaseModel
from social.models import Post
from django.contrib.contenttypes.fields import GenericRelation

from tagging.models import TaggedItem

User = get_user_model()


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments',
                             null=True, blank=True)
    content = models.TextField(default='No content')

    tags = GenericRelation(TaggedItem, related_query_name='comments')

    def __str__(self):
        return self.content[:20]
