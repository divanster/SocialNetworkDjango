# backend/core/models/base_models.py

from django.db import models, transaction
import uuid
import os
from django.utils import timezone
import logging
from django.core.exceptions import ValidationError
import re
from django.conf import settings

from core.signals import soft_delete, restore  # Import custom signals

logger = logging.getLogger(__name__)


# ===========================
# SoftDeleteManager with Transaction Management
# ===========================

class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """
        Returns all objects, including soft-deleted ones.
        """
        return super().get_queryset()

    @transaction.atomic
    def hard_delete(self, queryset):
        """
        Permanently deletes the given queryset.
        """
        queryset.delete()


# ===========================
# SoftDeleteModel with Custom Signals
# ===========================

class SoftDeleteModel(models.Model):
    """
    Abstract model implementing soft deletion.
    Instead of deleting records, it marks them as deleted.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()  # Filters out soft-deleted items.
    all_objects = models.Manager()  # Includes all items, including soft-deleted ones.

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the object by setting is_deleted to True and recording the deletion time.
        Emits a custom soft_delete signal.
        """
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
            logger.info(f"Soft-deleted {self.__class__.__name__} with ID {self.id}.")

            # Optionally, cascade soft delete to related objects
            self._cascade_soft_delete()

            # Emit soft_delete signal
            soft_delete.send(sender=self.__class__, instance=self)
        else:
            logger.warning(
                f"{self.__class__.__name__} with ID {self.id} is already soft-deleted."
            )

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the object from the database.
        Logs the hard deletion.
        """
        super().delete(using=using, keep_parents=keep_parents)
        logger.info(f"Hard-deleted {self.__class__.__name__} with ID {self.id}.")

    def restore(self):
        """
        Restore a soft-deleted object.
        Emits a custom restore signal.
        """
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save()
            logger.info(f"Restored {self.__class__.__name__} with ID {self.id}.")

            # Optionally, restore related objects
            self._cascade_restore()

            # Emit restore signal
            restore.send(sender=self.__class__, instance=self)
        else:
            logger.warning(
                f"{self.__class__.__name__} with ID {self.id} is not deleted."
            )

    def _cascade_soft_delete(self):
        """
        Override this method in subclasses to perform cascading soft deletes.
        """
        pass

    def _cascade_restore(self):
        """
        Override this method in subclasses to perform cascading restores.
        """
        pass

    @classmethod
    @transaction.atomic
    def bulk_soft_delete(cls, queryset):
        """
        Soft delete multiple objects at once.
        Emits a soft_delete signal for each instance.
        """
        now = timezone.now()
        updated_count = queryset.update(is_deleted=True, deleted_at=now)
        logger.info(f"Bulk soft-deleted {updated_count} {cls.__name__} objects.")

        # Emit soft_delete signal for each instance
        for instance in queryset:
            soft_delete.send(sender=cls, instance=instance)

    @classmethod
    @transaction.atomic
    def bulk_hard_delete(cls, queryset):
        """
        Hard delete multiple objects at once.
        Logs the hard deletion.
        """
        deleted_count, _ = queryset.delete()
        logger.info(f"Bulk hard-deleted {deleted_count} {cls.__name__} objects.")


# ===========================
# BaseModel for Timestamp Management
# ===========================

class BaseModel(models.Model):
    """
    Abstract base model adding created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


# ===========================
# UUIDModel for UUID Primary Key
# ===========================

class UUIDModel(models.Model):
    """
    Abstract base model adding a UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


# ===========================
# FilePathModel with Enhanced Security
# ===========================

class FilePathModel(models.Model):
    """
    Abstract base model providing a method to generate secure file paths for uploads.
    """

    def generate_file_path(self, filename, subfolder=''):
        """
        Generates a secure file path for uploaded files.

        Parameters:
            filename (str): The original filename.
            subfolder (str): Optional subfolder path based on related objects.

        Returns:
            str: The generated file path.
        """
        # Prevent path traversal
        if '..' in filename or filename.startswith('/'):
            raise ValidationError("Invalid filename.")

        # Extract and validate file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower().strip('.')
        allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'])
        if ext not in allowed_extensions:
            raise ValidationError(f"Unsupported file extension: {ext}")

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{ext}"

        # Construct the full file path
        if subfolder:
            # Sanitize subfolder to prevent path traversal
            sanitized_subfolder = re.sub(r'[^a-zA-Z0-9_/.-]', '_', subfolder)
            return os.path.join('uploads', sanitized_subfolder, unique_filename)

        return os.path.join('uploads', unique_filename)

    class Meta:
        abstract = True

    # Removed unnecessary save method as it didn't add any functionality
