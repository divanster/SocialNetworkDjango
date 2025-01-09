from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.utils import timezone
from django.conf import settings
from core.models.base_models import (
    BaseModel,
    UUIDModel,
    SoftDeleteModel,
    FilePathModel
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from phonenumber_field.modelfields import PhoneNumberField
import logging

logger = logging.getLogger(__name__)


# ===========================
# Custom User and Profile
# ===========================

# Define CustomUserManager
class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling the creation of User and Superuser.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Creates and returns a regular user with an email, username, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email address')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info(f"Created user {user.email}")
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Creates and returns a superuser with the specified email,
        username, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        superuser = self.create_user(email, username, password, **extra_fields)
        logger.info(f"Created superuser {superuser.email}")
        return superuser


# Define CustomUser
class CustomUser(UUIDModel, BaseModel, SoftDeleteModel, AbstractBaseUser,
                 PermissionsMixin):
    """
    Custom user model that uses email instead of username for authentication.
    Inherits from UUIDModel, BaseModel, SoftDeleteModel, AbstractBaseUser, and PermissionsMixin
    to utilize UUID primary keys, timestamp tracking, and soft deletion.
    """
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def clean(self):
        """
        Custom validation for CustomUser fields.
        Ensures that the email is valid and not already in use.
        """
        if self.email:
            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError("Invalid email address.")

    def _cascade_soft_delete(self):
        """
        Soft delete related UserProfile when the user is soft-deleted.
        """
        if hasattr(self, 'profile'):
            self.profile.delete()

    def _cascade_restore(self):
        """
        Restore related UserProfile when the user is restored.
        """
        if hasattr(self, 'profile'):
            self.profile.restore()


def user_profile_picture_file_path(instance, filename):
    """
    Generates a file path for a new user profile picture using FilePathModel's generate_file_path.
    """
    return instance.generate_file_path(
        filename,
        subfolder=f"user_{instance.user.id}/profile_pictures"
    )


# Define UserProfile
class UserProfile(UUIDModel, BaseModel, SoftDeleteModel, FilePathModel):
    """
    UserProfile model that stores additional information about the user.
    Inherits from UUIDModel, BaseModel, SoftDeleteModel, and FilePathModel.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified'),
    ]

    RELATIONSHIP_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
        ('P', 'In a relationship'),
        ('C', 'Complicated'),
    ]

    # One-to-one relationship with the custom user model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_file_path,
        null=True,
        blank=True,
        default='static/default_images/profile_picture.png'
    )
    bio = models.TextField(blank=True)
    phone = PhoneNumberField(blank=True, null=True, help_text="User's phone number")
    town = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    relationship_status = models.CharField(
        max_length=1,
        choices=RELATIONSHIP_STATUS_CHOICES,
        default='S'
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['user'], name='user_profile_user_idx'),
            models.Index(fields=['gender'], name='gender_idx'),
            models.Index(fields=['relationship_status'],
                         name='relationship_status_idx'),
        ]

    def __str__(self):
        return f'{self.user.username} Profile'

    def clean(self):
        """
        Custom validation for UserProfile fields.
        Ensures that the date_of_birth is not set in the future.
        """
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")

    def _cascade_soft_delete(self):
        """
        Override to soft delete related objects if any.
        For example, if the profile has related posts or activities.
        """
        # Example: Soft delete related posts
        # self.posts.all().update(is_deleted=True, deleted_at=timezone.now())
        pass

    def _cascade_restore(self):
        """
        Override to restore related objects if any.
        """
        # Example: Restore related posts
        # self.posts.all_with_deleted().filter(is_deleted=True).update(is_deleted=False, deleted_at=None)
        pass
