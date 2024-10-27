from django.db import models
import uuid
import os
from mongoengine import Document, DateTimeField as MongoDateTimeField, \
    BooleanField as MongoBooleanField, UUIDField as MongoUUIDField
from datetime import datetime
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.conf import settings
from django.db.models.signals import pre_save, post_save


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


# ===========================
# BaseModel for MongoEngine
# ===========================

class MongoBaseModel(Document):
    """
    Base model for MongoEngine-based models using MongoDB.
    Includes created and updated timestamps.
    """
    created_at = MongoDateTimeField(default=datetime.utcnow)
    updated_at = MongoDateTimeField(default=datetime.utcnow)

    meta = {
        'db_alias': 'social_db',
        'abstract': True,
        'ordering': ['-created_at'],
    }

    def save(self, *args, **kwargs):
        """
        Override save to update 'updated_at' field.
        """
        if self.pk:
            self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class MongoSoftDeleteModel(Document):
    """
    Base model to add soft delete capability for MongoEngine models.
    """
    is_deleted = MongoBooleanField(default=False)

    meta = {
        'abstract': True,
    }

    def soft_delete(self):
        """
        Soft delete by setting `is_deleted` to True.
        """
        self.is_deleted = True
        self.save()


class MongoUUIDModel(Document):
    """
    Base model to add UUID primary key for MongoEngine models.
    """
    id = MongoUUIDField(binary=False, primary_key=True, default=uuid.uuid4)

    meta = {
        'abstract': True,
    }
