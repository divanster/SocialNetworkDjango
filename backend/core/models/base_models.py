from django.db import models
import uuid
import os
from django.utils import timezone


# ===========================
# BaseModel for Django ORM
# ===========================

class BaseModel(models.Model):
    """
    Base model for Django-based models using PostgreSQL.
    Includes created and updated timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Override save to automatically update the `updated_at` field.
        """
        if not self._state.adding:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class SoftDeleteModel(models.Model):
    """
    Base model to add soft delete capability for Django ORM models.
    """
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete by setting `is_deleted` to True.
        """
        self.is_deleted = True
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the object.
        """
        super().delete(using=using, keep_parents=keep_parents)


class UUIDModel(models.Model):
    """
    Base model to add UUID primary key for Django ORM models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class FilePathModel(models.Model):
    """
    Base model to handle file paths for file uploads.
    """

    def generate_file_path(self, filename):
        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4()}.{ext}'
        return os.path.join('uploads/', filename)

    class Meta:
        abstract = True
