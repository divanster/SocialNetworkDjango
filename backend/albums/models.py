from django.db import models
from core.models.base_models import BaseModel, FilePathModel
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from tagging.models import TaggedItem

User = get_user_model()


def album_image_file_path(instance, filename):
    return instance.generate_file_path(filename)


class Album(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    tags = GenericRelation(TaggedItem, related_query_name='photos')


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Photo(FilePathModel, BaseModel):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=album_image_file_path)
    description = models.TextField(blank=True)

    tags = GenericRelation(TaggedItem, related_query_name='photos')


    def __str__(self):
        return f"Photo in {self.album.title}"
