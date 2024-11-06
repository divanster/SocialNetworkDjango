# elasticsearch_service/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from social.models import Post
from comments.models import Comment
from pages.models import Page
from albums.models import Album
from stories.models import Story
from .documents import PostDocument, CommentDocument, PageDocument, AlbumDocument, \
    StoryDocument


@receiver(post_save, sender=Post)
def update_post_index(sender, instance, **kwargs):
    PostDocument().update(instance)


@receiver(post_delete, sender=Post)
def delete_post_index(sender, instance, **kwargs):
    PostDocument().delete(instance)


@receiver(post_save, sender=Comment)
def update_comment_index(sender, instance, **kwargs):
    CommentDocument().update(instance)


@receiver(post_delete, sender=Comment)
def delete_comment_index(sender, instance, **kwargs):
    CommentDocument().delete(instance)


@receiver(post_save, sender=Page)
def update_page_index(sender, instance, **kwargs):
    PageDocument().update(instance)


@receiver(post_delete, sender=Page)
def delete_page_index(sender, instance, **kwargs):
    PageDocument().delete(instance)


@receiver(post_save, sender=Album)
def update_album_index(sender, instance, **kwargs):
    AlbumDocument().update(instance)


@receiver(post_delete, sender=Album)
def delete_album_index(sender, instance, **kwargs):
    AlbumDocument().delete(instance)


@receiver(post_save, sender=Story)
def update_story_index(sender, instance, **kwargs):
    StoryDocument().update(instance)


@receiver(post_delete, sender=Story)
def delete_story_index(sender, instance, **kwargs):
    StoryDocument().delete(instance)
