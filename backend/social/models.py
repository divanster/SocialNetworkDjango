# social/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Import visibility choices

User = get_user_model()

class PostQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC)
        else:
            public_posts = self.filter(visibility=VisibilityChoices.PUBLIC)
            friends_posts = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                author__in=get_friends(user)
            )
            own_posts = self.filter(author=user)
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
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Author of the post"
    )
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        help_text="Visibility of the post"
    )
    tags = GenericRelation(TaggedItem, related_query_name='posts')

    objects = PostManager()  # Use custom manager

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
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
