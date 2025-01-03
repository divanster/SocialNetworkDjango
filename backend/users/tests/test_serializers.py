from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from users.models import UserProfile
from users.serializers import CustomUserSerializer, UserProfileSerializer
from tagging.models import TaggedItem

User = get_user_model()


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        self.profile = UserProfile.objects.create(user=self.user)

    def test_user_profile_serialization(self):
        """Test that UserProfileSerializer correctly serializes the profile data"""
        serializer = UserProfileSerializer(instance=self.profile)
        data = serializer.data
        self.assertEqual(data['first_name'], '')
        self.assertEqual(data['last_name'], '')
        self.assertEqual(data['gender'], 'N')
        # Add more assertions for other fields as needed

    def test_user_profile_deserialization(self):
        """Test that UserProfileSerializer correctly deserializes and updates the
        profile data"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'bio': 'Test bio',
            'phone': '1234567890',
            'town': 'Test Town',
            'country': 'Test Country',
            'relationship_status': 'S',
            'tagged_user_ids': []
        }
        request = self.factory.get('/')
        request.user = self.user
        serializer = UserProfileSerializer(
            instance=self.profile, data=data, context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.gender, 'M')
        self.assertEqual(profile.date_of_birth.strftime('%Y-%m-%d'), '1990-01-01')

    def test_user_profile_update_with_tagging(self):
        """Test updating UserProfile with tagged user IDs"""
        another_user = User.objects.create_user(
            email='another@example.com',
            username='anotheruser',
            password='anotherpassword'
        )
        data = {
            'bio': 'Updated bio',
            'tagged_user_ids': [str(another_user.id)]
        }
        request = self.factory.patch('/')
        request.user = self.user
        serializer = UserProfileSerializer(
            instance=self.profile, data=data, context={'request': request}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        # Check that the TaggedItem has been created
        tagged_items = TaggedItem.objects.filter(
            tagged_user=another_user,
            tagged_by=self.user,
            content_type__model='userprofile',
            object_id=self.profile.id
        )
        self.assertTrue(tagged_items.exists())

    def test_invalid_gender_choice(self):
        """Test setting an invalid gender choice raises a validation error"""
        data = {
            'gender': 'X'  # Invalid gender choice
        }
        serializer = UserProfileSerializer(instance=self.profile, data=data,
                                           partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('gender', serializer.errors)


class CustomUserSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_user(self):
        """Test that CustomUserSerializer can successfully create a new user"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'profile': {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'gender': 'F',
                'date_of_birth': '1995-05-15',
                'bio': 'Hello, world!',
                'phone': '555-5555',
                'town': 'Testville',
                'country': 'Testland',
                'relationship_status': 'S',
                'tagged_user_ids': []
            }
        }
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpassword123'))
        self.assertEqual(user.profile.first_name, 'Jane')
        self.assertEqual(user.profile.last_name, 'Doe')

    def test_user_password_mismatch(self):
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'password': 'password123',
            'password2': 'password456',  # Mismatched password
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(
            serializer.errors['password'][0].code, 'password_mismatch'
        )

    def test_update_user(self):
        """Test updating an existing user's email and profile information"""
        user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='password123'
        )
        data = {
            'email': 'updated@example.com',
            'profile': {
                'bio': 'Updated bio',
            }
        }
        request = self.factory.patch('/')
        request.user = user
        serializer = CustomUserSerializer(
            instance=user, data=data, context={'request': request}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        user.refresh_from_db()
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.profile.bio, 'Updated bio')

    def test_create_user_unique_email(self):
        """Test that creating a user with a duplicate email raises a validation error"""
        User.objects.create_user(
            email='existing@example.com',
            username='existinguser',
            password='password123'
        )
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'password123',
            'password2': 'password123',
        }
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_update_password(self):
        """Test updating user's password"""
        user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='oldpassword123'
        )
        data = {
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        request = self.factory.patch('/')
        request.user = user
        serializer = CustomUserSerializer(
            instance=user, data=data, context={'request': request}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
