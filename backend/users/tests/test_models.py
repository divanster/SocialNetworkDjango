from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import UserProfile
from django.utils import timezone

User = get_user_model()

class CustomUserManagerTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = 'testuser@example.com'
        username = 'testuser'
        password = 'testpassword'
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'testuser@EXAMPLE.COM'
        user = User.objects.create_user(email=email, username='testuser', password='testpassword')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, username='testuser', password='testpassword')

    def test_create_new_superuser(self):
        email = 'superuser@example.com'
        username = 'superuser'
        password = 'superpassword'
        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='superuser@example.com',
                username='superuser',
                password='superpassword',
                is_staff=False
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='superuser@example.com',
                username='superuser',
                password='superpassword',
                is_superuser=False
            )

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )

    def test_user_profile_created(self):
        # Assuming you have a signal that creates UserProfile on user creation
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_user_profile_str(self):
        profile = UserProfile.objects.get(user=self.user)
        expected_str = f'{self.user.username} Profile'
        self.assertEqual(str(profile), expected_str)

    def test_profile_picture_url_with_picture(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.profile_picture = 'path/to/picture.jpg'
        self.assertEqual(profile.profile_picture_url, profile.profile_picture.url)

    def test_profile_picture_url_without_picture(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.profile_picture = ''
        self.assertEqual(profile.profile_picture_url, '/static/default_images/default_profile.jpg')

    def test_date_of_birth_in_future_raises_validation_error(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = timezone.now().date() + timezone.timedelta(days=1)
        with self.assertRaises(ValidationError):
            profile.clean()

    def test_valid_date_of_birth(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = timezone.now().date() - timezone.timedelta(days=1000)
        # Should not raise an error
        try:
            profile.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_gender_choice(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.gender = 'M'
        profile.save()
        self.assertEqual(profile.gender, 'M')

    def test_relationship_status_choice(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.relationship_status = 'M'
        profile.save()
        self.assertEqual(profile.relationship_status, 'M')
