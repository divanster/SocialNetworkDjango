# backend/users/models.py

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from core.models.base_models import BaseModel, UUIDModel
from django.conf import settings


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
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
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

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email instead of username for authentication.
    """

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


def user_profile_picture_file_path(instance, filename):
    """
    Generates a file path for a new user profile picture.
    """
    import uuid
    import os
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/profile_pictures/', filename)


class UserProfile(UUIDModel, BaseModel):  # Inherit UUIDModel and BaseModel
    """
    UserProfile model that stores additional information about the user.
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profile')

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    date_of_birth = models.DateField(null=True, blank=True)

    # ImageField to store profile picture, using the file path function
    profile_picture = models.ImageField(upload_to=user_profile_picture_file_path,
                                        null=True, blank=True,
                                        default='static/default_images'
                                                '/profile_picture.png')

    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    relationship_status = models.CharField(max_length=1,
                                           choices=RELATIONSHIP_STATUS_CHOICES,
                                           default='S')

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def profile_picture_url(self):
        """
        Returns the URL of the user's profile picture, falling back to a default image if none exists.
        """
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/default_images/default_profile.jpg'

    def clean(self):
        """
        Custom validation to ensure the date of birth is not set in the future.
        """
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError(_('Date of birth cannot be in the future.'))
        super().clean()
