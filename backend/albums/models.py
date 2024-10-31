from django.db import models
from django.contrib.auth import get_user_model
from core.models.base_models import UUIDModel, BaseModel, SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Import visibility choices
import uuid
import os

User = get_user_model()


def album_image_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(f'uploads/album/{instance.album.user.id}/', filename)


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

    def get_photos(self):
        """
        Retrieve all photos related to this album.
        """
        try:
            return self.photos.all()
        except Exception as e:
            logging.error(f"Error retrieving photos for album {self.id}: {e}")
            return []


class PhotoQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_anonymous:
            return self.filter(album__visibility=VisibilityChoices.PUBLIC)
        else:
            public_photos = self.filter(album__visibility=VisibilityChoices.PUBLIC)
            friends_photos = self.filter(
                album__visibility=VisibilityChoices.FRIENDS,
                album__user__in=get_friends(user)
            )
            own_photos = self.filter(album__user=user)
            return public_photos | friends_photos | own_photos


class PhotoManager(models.Manager):
    def get_queryset(self):
        return PhotoQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Photo(UUIDModel, BaseModel):
    """
    Represents a photo within an album with visibility settings derived from the album.
    """
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos',
        help_text="Album to which this photo belongs"
    )
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)
    tags = GenericRelation(TaggedItem, related_query_name='photos')

    objects = PhotoManager()  # Use custom manager

    class Meta:
        db_table = 'photos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Photo in album '{self.album.title}'"

    def get_image_url(self):
        """
        Retrieve the URL of the image file.
        """
        if self.image:
            return self.image.url
        return None
