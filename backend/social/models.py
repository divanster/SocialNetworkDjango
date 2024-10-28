from django.db import models
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from django.contrib.auth import get_user_model
from tagging.models import TaggedItem
import uuid
import os

User = get_user_model()

# Helper function for generating file paths for post images
def post_image_file_path(instance, filename):
    """
    Helper function to generate a file path for new post images.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


class Post(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Main model for storing Posts.
    Utilizes PostgreSQL to store data with better consistency and relational integrity.
    """
    title = models.CharField(max_length=255, help_text="Title of the post")
    content = models.TextField(help_text="Content of the post", blank=True, null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Author of the post"
    )
    tags = models.ManyToManyField(
        TaggedItem,
        blank=True,
        related_name='posts',
        help_text="Tags related to the post"
    )

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),  # Index for efficient author-based querying
            models.Index(fields=['title']),  # Index to speed up search by title
        ]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """
        Calculate the average rating of the post.
        """
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0


class PostImage(UUIDModel, BaseModel):
    """
    Model to store image information related to a post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="Post associated with this image"
    )
    image = models.ImageField(upload_to=post_image_file_path, help_text="Path to the image file")

    class Meta:
        db_table = 'post_images'
        ordering = ['-created_at']

    def __str__(self):
        return f"Image for Post '{self.post.title}'"


class Rating(UUIDModel, BaseModel):
    """
    Model for storing Ratings related to a Post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="Post associated with this rating"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_given',
        help_text="User who gave the rating"
    )
    value = models.PositiveSmallIntegerField(
        help_text="Rating value between 1 and 5",
        choices=[(i, i) for i in range(1, 6)]
    )

    class Meta:
        db_table = 'ratings'
        ordering = ['-created_at']
        unique_together = ('post', 'user')  # A user can only rate a post once

    def __str__(self):
        return f"Rating {self.value} Stars by User '{self.user.username}'"


class Story(UUIDModel, BaseModel):
    """
    A model representing a user's story.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stories',
        help_text="User who created the story"
    )
    content = models.TextField(
        help_text="Text content of the story. Keep it short and engaging.",
        blank=True,
        null=True
    )
    media_type = models.CharField(
        max_length=10,
        choices=[('image', 'Image'), ('video', 'Video'), ('text', 'Text')],
        help_text="Type of the story content",
        default='text'
    )
    media_url = models.URLField(
        help_text="URL of the media for the story (if applicable)",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, help_text="Is the story active or has it expired?")
    viewed_by = models.ManyToManyField(
        User,
        related_name='viewed_stories',
        blank=True,
        help_text="Users who have viewed this story"
    )
    tags = models.ManyToManyField(
        TaggedItem,
        blank=True,
        related_name='stories',
        help_text="Tags related to the story"
    )

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),  # Index for efficient user-based querying
            models.Index(fields=['created_at']),  # Index for story ordering by date
        ]

    def __str__(self):
        return f"Story by {self.user.username} at {self.created_at}"

    def deactivate_story(self):
        """
        Mark the story as inactive after the expiration period.
        """
        self.is_active = False
        self.save()

    def add_tag(self, tagged_user, tagged_by):
        """
        Adds a tag to this story.
        """
        TaggedItem.objects.create(
            story=self,
            tagged_user=tagged_user,
            tagged_by=tagged_by
        )

    def get_tags(self):
        """
        Retrieves all tags related to this story.
        """
        return self.tags.all()

    def add_view(self, user):
        """
        Add a user to the list of those who have viewed the story.
        """
        self.viewed_by.add(user)
