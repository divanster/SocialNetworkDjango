# backend/social/models.py

import uuid
import os
import logging
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from tagging.models import TaggedItem
from comments.models import Comment
from core.choices import VisibilityChoices  # Import visibility choices
from users.models import CustomUser

# Initialize logger for this module
logger = logging.getLogger(__name__)

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """
        Returns a queryset of posts visible to the given user based on visibility settings.
        """
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC)
        else:
            public_posts = self.filter(visibility=VisibilityChoices.PUBLIC)
            friends_posts = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                user__in=get_friends(user)
            )
            own_posts = self.filter(user=user)
            return public_posts | friends_posts | own_posts


def get_friends(user):
    """
    Retrieves all friends of a given user.
    """
    from friends.models import Friendship  # Imported here to avoid circular imports
    friends = Friendship.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    )
    friend_ids = set()
    for friendship in friends:
        friend_ids.add(friendship.user1_id)
        friend_ids.add(friendship.user2_id)
    friend_ids.discard(user.id)
    return User.objects.filter(id__in=friend_ids)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Post(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Main model for storing Posts with visibility settings.
    Inherits from UUIDModel, SoftDeleteModel, and BaseModel to utilize UUID primary keys,
    soft deletion, and timestamp tracking.
    """
    title = models.CharField(max_length=255, help_text="Title of the post")
    content = models.TextField(help_text="Content of the post", blank=True, null=True)
    user = models.ForeignKey(
        CustomUser,
        related_name='posts',
        on_delete=models.CASCADE,
        help_text="Author of the post"
    )
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        help_text="Visibility of the post"
    )
    tags = GenericRelation(TaggedItem, related_query_name='posts')
    comments = GenericRelation(Comment, related_query_name='posts')

    objects = PostManager()  # Use custom manager

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user'], name='post_user_idx'),
            models.Index(fields=['title'], name='post_title_idx'),
            models.Index(fields=['visibility'], name='post_visibility_idx'),
        ]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """
        Calculates the average rating of the post.
        """
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0

    def _cascade_soft_delete(self):
        """
        Soft deletes related PostImages, Ratings, and Comments when the post is soft-deleted.
        """
        logger.debug(f"Cascading soft delete for Post ID: {self.id}")
        self.images.all().delete()
        self.ratings.all().delete()
        self.comments.all().delete()

    def _cascade_restore(self):
        """
        Restores related PostImages, Ratings, and Comments when the post is restored.
        """
        logger.debug(f"Cascading restore for Post ID: {self.id}")
        self.images.all_with_deleted().filter(is_deleted=True).restore()
        self.ratings.all_with_deleted().filter(is_deleted=True).restore()
        self.comments.all_with_deleted().filter(is_deleted=True).restore()


def post_image_file_path(instance, filename):
    """
    Helper function to generate a file path for new post images.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


class PostImage(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Model to store image information related to a post.
    Inherits from UUIDModel, SoftDeleteModel, and BaseModel to utilize UUID primary keys,
    soft deletion, and timestamp tracking.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="Post associated with this image"
    )
    image = models.ImageField(
        upload_to=post_image_file_path,
        help_text="Path to the image file"
    )

    class Meta:
        db_table = 'post_images'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post'], name='post_idx'),
        ]

    def __str__(self):
        return f"Image for Post '{self.post.title}'"

    def _cascade_soft_delete(self):
        """
        Override to handle any related objects if necessary.
        """
        logger.debug(f"Cascading soft delete for PostImage ID: {self.id}")
        # Implement if there are related objects

    def _cascade_restore(self):
        """
        Override to handle any related objects if necessary.
        """
        logger.debug(f"Cascading restore for PostImage ID: {self.id}")
        # Implement if there are related objects


class Rating(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Model for storing Ratings related to a Post.
    Inherits from UUIDModel, SoftDeleteModel, and BaseModel to utilize UUID primary keys,
    soft deletion, and timestamp tracking.
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
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post'], name='rating_post_idx'),
            models.Index(fields=['user'], name='rating_user_idx'),
        ]

    def __str__(self):
        return f"Rating {self.value} Stars by User '{self.user.username}'"

    def _cascade_soft_delete(self):
        """
        Override to handle any related objects if necessary.
        """
        logger.debug(f"Cascading soft delete for Rating ID: {self.id}")
        # Implement if there are related objects

    def _cascade_restore(self):
        """
        Override to handle any related objects if necessary.
        """
        logger.debug(f"Cascading restore for Rating ID: {self.id}")
        # Implement if there are related objects
