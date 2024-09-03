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
            'email': 'uniqueuser2@example.com',
            'username': 'uniqueuser2',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Just a test user.',
            'phone': '1234567890',
            'town': 'Test Town',
            'country': 'Test Country',
            'relationship_status': 'S'
        }
        serializer = CustomUserSerializer(data=user_data)
        print(f"Debug: Initial data for serializer: {user_data}")  # Debug output
        self.assertTrue(serializer.is_valid(), serializer.errors)
        print(f"Debug: Validated data: {serializer.validated_data}")  # Debug output
        try:
            user = serializer.save()
            print(f"Debug: Created user: {user}")  # Debug output
            self.assertEqual(user.email, user_data['email'])
            self.assertEqual(user.username, user_data['username'])

            # Check if user profile is correctly created
            profile = UserProfile.objects.get(user=user)
            print(f"Debug: Created user profile: {profile.__dict__}")  # Debug output
            self.assertEqual(profile.first_name, user_data['first_name'])
            self.assertEqual(profile.last_name, user_data['last_name'])
            self.assertEqual(profile.bio, user_data['bio'])
            self.assertEqual(profile.phone, user_data['phone'])
            self.assertEqual(profile.town, user_data['town'])
            self.assertEqual(profile.country, user_data['country'])
            self.assertEqual(profile.relationship_status,
                             user_data['relationship_status'])
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
