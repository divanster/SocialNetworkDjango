from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from tagging.models import TaggedItem
from comments.models import Comment
from core.choices import VisibilityChoices  # Import visibility choices
import uuid
import os
from users.models import CustomUser

User = get_user_model()


class PostQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC)
        else:
            public_posts = self.filter(visibility=VisibilityChoices.PUBLIC)
            friends_posts = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                user__in=get_friends(user)  # Changed 'author' to 'user'
            )
            own_posts = self.filter(user=user)  # Changed 'author' to 'user'
            return public_posts | friends_posts | own_posts


def get_friends(user):
    from friends.models import Friendship
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
    """
    title = models.CharField(max_length=255, help_text="Title of the post")
    content = models.TextField(help_text="Content of the post", blank=True, null=True)
    user = models.ForeignKey(CustomUser,
                             related_name='posts',
                             on_delete=models.CASCADE)
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
            models.Index(fields=['user']),  # Changed 'author' to 'user'
            models.Index(fields=['title']),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0


# ===========================
# PostImage Model
# ===========================

def post_image_file_path(instance, filename):
    """
    Helper function to generate a file path for new post images.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


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
    image = models.ImageField(
        upload_to=post_image_file_path,
        help_text="Path to the image file"
    )

    class Meta:
        db_table = 'post_images'
        ordering = ['-created_at']

    def __str__(self):
        return f"Image for Post '{self.post.title}'"


# ===========================
# Rating Model
# ===========================

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
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Rating {self.value} Stars by User '{self.user.username}'"
