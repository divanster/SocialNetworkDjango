from django.test import TestCase, override_settings
from users.serializers import CustomUserSerializer, UserProfileSerializer
from users.models import UserProfile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class UserSerializerTests(TestCase):

    def setUp(self):
        # Ensure a clean state before each test
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_user_serializer(self):
        user_data = {
            'email': 'uniqueuser2@example.com',  # Ensure unique email for each test
            'username': 'uniqueuser2',  # Ensure unique username for each test
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'profile': {
                'first_name': 'Test',
                'last_name': 'User',
                'bio': 'Just a test user.'
            }
        }
        serializer = CustomUserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        try:
            user = serializer.save()
            self.assertEqual(user.email, user_data['email'])
            self.assertEqual(user.username, user_data['username'])
            # Check if user profile is correctly created
            profile = UserProfile.objects.get(user=user)
            self.assertEqual(profile.first_name, 'Test')
            self.assertEqual(profile.last_name, 'User')
            self.assertEqual(profile.bio, 'Just a test user.')
        except ValidationError as e:
            self.fail(f'User creation failed with error: {e}')
        except Exception as e:
            self.fail(f'Unexpected error: {e}')

    def test_user_profile_serializer(self):
        user = User.objects.create_user(email='uniqueuser3@example.com',
                                        username='uniqueuser3', password='testpass123')
        profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(profile)
        self.assertEqual(serializer.data['first_name'], profile.first_name)
