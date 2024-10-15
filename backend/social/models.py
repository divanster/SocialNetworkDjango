# social/models.py

from django.db import models
from core.models.base_models import BaseModel
from django.core.exceptions import ValidationError
import uuid


def post_image_file_path(instance, filename):
    import os
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


class Post(BaseModel):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author_id = models.IntegerField()
    author_username = models.CharField(max_length=150)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = Rating.objects.using('social_db').filter(post_id=self.post_id)
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0


class PostImage(BaseModel):
    post_id = models.UUIDField()
    image = models.ImageField(upload_to=post_image_file_path)

    def __str__(self):
        return f"Image for Post ID {self.post_id}"


class Rating(BaseModel):
    post_id = models.UUIDField()
    user_id = models.IntegerField()
    user_username = models.CharField(max_length=150)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('post_id', 'user_id')

    def clean(self):
        if self.value < 1 or self.value > 5:
            raise ValidationError('Rating value must be between 1 and 5.')

    def __str__(self):
        return f"Rating {self.value} Stars for Post ID {self.post_id}"
