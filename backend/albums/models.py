# albums/models.py

from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Import visibility choices

User = get_user_model()


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


class AlbumQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_anonymous:
            return self.filter(visibility=VisibilityChoices.PUBLIC)
        else:
            public_albums = self.filter(visibility=VisibilityChoices.PUBLIC)
            friends_albums = self.filter(
                visibility=VisibilityChoices.FRIENDS,
                user__in=get_friends(user)
            )
            own_albums = self.filter(user=user)
            return public_albums | friends_albums | own_albums


class AlbumManager(models.Manager):
    def get_queryset(self):
        return AlbumQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Album(UUIDModel, SoftDeleteModel, BaseModel):
    """
    Represents an album with related photos and visibility settings.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='albums',
        help_text="User who owns the album"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        help_text="Visibility of the album"
    )
    tags = GenericRelation(TaggedItem, related_query_name='albums')

    objects = AlbumManager()  # Use custom manager

    class Meta:
        db_table = 'albums'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'],
                                    name='unique_user_album_title')
        ]
        indexes = [
            models.Index(fields=['user'], name='user_idx'),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return self.title
