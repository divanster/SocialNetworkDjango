from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


def user_profile_picture_file_path(instance, filename):
    """Generate file path for new user profile picture"""
    import uuid
    import os
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/profile_pictures/', filename)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(upload_to=user_profile_picture_file_path, null=True, blank=True,
                                        default='static/default_images/profile_picture.png')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    date_of_birth = models.DateField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Ensure username is set to the part of email before "@" if not provided
        if not self.username:
            email_username = self.email.split('@')[0]
            self.username = email_username

        # Ensure full name is populated based on first_name and last_name if not provided
        if not self.first_name and not self.last_name:
            self.first_name = self.email.split('@')[0]  # Fallback to part of email

        # Perform any additional validation or cleanup here
        super(CustomUser, self).save(*args, **kwargs)

    def clean(self):
        # Add custom validation if needed
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError(_('Date of birth cannot be in the future.'))
        super().clean()

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/default_images/default_profile.jpg'
