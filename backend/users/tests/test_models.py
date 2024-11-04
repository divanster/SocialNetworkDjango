from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import UserProfile
from django.utils import timezone

User = get_user_model()


class CustomUserManagerTests(TestCase):

    def tearDown(self):
        User.objects.all().delete()
        UserProfile.objects.all().delete()

    def setUp(self):
        self.email = 'testuser@example.com'
        self.username = 'testuser'
        self.password = 'testpassword'

    def test_create_user_with_email_successful(self):
        email = 'uniqueuser@example.com'
        username = 'uniqueuser'
        password = 'testpassword'
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        # Correct assertions to match created user values
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)  # Use the correct username variable
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test if the email for a new user is normalized"""
        email = 'testuser@EXAMPLE.COM'
        user = User.objects.create_user(email=email, username=self.username,
                                        password=self.password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, username=self.username,
                                     password=self.password)

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = User.objects.create_superuser(
            email=self.email,
            username=self.username,
            password=self.password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test creating a superuser with is_staff=False raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=self.email,
                username=self.username,
                password=self.password,
                is_staff=False
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test creating a superuser with is_superuser=False raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=self.email,
                username=self.username,
                password=self.password,
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
        """Test that a user profile is created when a new user is created"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)

    def test_user_profile_str(self):
        """Test the user profile string representation"""
        profile = UserProfile.objects.get(user=self.user)
        expected_str = f'{self.user.username} Profile'
        self.assertEqual(str(profile), expected_str)

    def test_profile_picture_default(self):
        """Test that a default profile picture is set correctly"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.profile_picture.name,
                         'static/default_images/profile_picture.png')

    def test_date_of_birth_in_future_raises_validation_error(self):
        """Test that setting date of birth in the future raises a validation error"""
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = timezone.now().date() + timezone.timedelta(days=1)
        with self.assertRaises(ValidationError):
            profile.clean()

    def test_valid_date_of_birth(self):
        """Test that setting a valid date of birth does not raise any error"""
        profile = UserProfile.objects.get(user=self.user)
        profile.date_of_birth = timezone.now().date() - timezone.timedelta(days=1000)
        try:
            profile.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_gender_choice(self):
        """Test setting a valid gender choice"""
        profile = UserProfile.objects.get(user=self.user)
        profile.gender = 'M'
        profile.save()
        self.assertEqual(profile.gender, 'M')

    def test_invalid_gender_choice(self):
        """Test setting an invalid gender choice raises an error"""
        profile = UserProfile.objects.get(user=self.user)
        with self.assertRaises(ValidationError):
            profile.gender = 'X'
            profile.full_clean()  # Ensure validation is triggered

    def test_relationship_status_choice(self):
        """Test setting a valid relationship status"""
        profile = UserProfile.objects.get(user=self.user)
        profile.relationship_status = 'M'
        profile.save()
        self.assertEqual(profile.relationship_status, 'M')

    def test_invalid_relationship_status_choice(self):
        """Test setting an invalid relationship status raises an error"""
        profile = UserProfile.objects.get(user=self.user)
        with self.assertRaises(ValidationError):
            profile.relationship_status = 'X'
            profile.full_clean()  # Ensure validation is triggered

    def test_profile_picture_custom_path(self):
        """Test that a custom profile picture path is set correctly"""
        profile = UserProfile.objects.get(user=self.user)
        profile.profile_picture = 'path/to/custom_picture.jpg'
        profile.save()
        self.assertEqual(profile.profile_picture.name, 'path/to/custom_picture.jpg')

    def test_profile_phone_field(self):
        """Test the optional phone field"""
        profile = UserProfile.objects.get(user=self.user)
        profile.phone = '+1234567890'
        profile.save()
        self.assertEqual(profile.phone, '+1234567890')

    def test_profile_town_country_fields(self):
        """Test setting town and country fields"""
        profile = UserProfile.objects.get(user=self.user)
        profile.town = 'New York'
        profile.country = 'USA'
        profile.save()
        self.assertEqual(profile.town, 'New York')
        self.assertEqual(profile.country, 'USA')
