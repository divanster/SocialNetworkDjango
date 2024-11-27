# ===========================
# Custom User and Profile
# ===========================
from django.db import models
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from core.models.base_models import BaseModel, UUIDModel
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from phonenumber_field.modelfields import PhoneNumberField


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


# Define CustomUser
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
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/profile_pictures/', filename)


# Define UserProfile
class UserProfile(UUIDModel, BaseModel):
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

    def __str__(self):
        return f'{self.user.username} Profile'

    def clean(self):
        """
        Custom validation for UserProfile fields.
        Ensures that the date_of_birth is not set in the future.
        """
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
