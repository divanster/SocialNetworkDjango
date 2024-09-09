import os
import uuid
from django.db import models
from core.models.base_models import BaseModel
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def post_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


class Tag(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0


class PostImage(BaseModel):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=post_image_file_path)

    def __str__(self):
        return f"{self.post.title} Image"


class Rating(BaseModel):
    post = models.ForeignKey(Post, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('post', 'user')

    def clean(self):
        if self.value < 1 or self.value > 5:
            raise ValidationError('Rating value must be between 1 and 5.')

    def __str__(self):
        return f"{self.post.title} - {self.value} Stars"
