from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from users.models import CustomUser, UserProfile
from users.serializers import CustomUserSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        self.user_token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        self.profile = UserProfile.objects.get(user=self.user)
        self.user_profile_url = reverse('userprofile-detail', kwargs={'pk': self.profile.pk})

    def test_retrieve_user_profile(self):
        """Test retrieving the profile of the authenticated user"""
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = UserProfileSerializer(self.profile)
        self.assertEqual(response.data, serializer.data)

    @patch('users.tasks.send_profile_update_notification.delay')
    def test_update_user_profile(self, mock_send_profile_update_notification):
        """Test updating user profile data"""
        data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'bio': 'Updated bio'
        }
        response = self.client.patch(self.user_profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'UpdatedFirstName')
        self.assertEqual(self.profile.last_name, 'UpdatedLastName')
        self.assertEqual(self.profile.bio, 'Updated bio')

        # Verify that the profile update task was called
        mock_send_profile_update_notification.assert_called_once_with(self.user.id)


class CustomUserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        self.user_token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        self.user_detail_url = reverse('customuser-detail', kwargs={'pk': self.user.pk})
        self.me_url = reverse('customuser-me')

    def test_retrieve_user(self):
        """Test retrieving the user details"""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CustomUserSerializer(self.user)
        self.assertEqual(response.data, serializer.data)

    @patch('users.tasks.send_profile_update_notification.delay')
    def test_update_user_via_me_endpoint(self, mock_send_profile_update_notification):
        """Test updating user data via 'me' endpoint"""
        data = {
            'username': 'updatedusername',
            'profile': {
                'bio': 'Updated bio through me endpoint'
            }
        }
        response = self.client.patch(self.me_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updatedusername')
        self.assertEqual(self.user.profile.bio, 'Updated bio through me endpoint')

        # Verify that the profile update task was called
        mock_send_profile_update_notification.assert_called_once_with(self.user.id)

    def test_get_me_endpoint(self):
        """Test retrieving the authenticated user's details via 'me' endpoint"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CustomUserSerializer(self.user)
        self.assertEqual(response.data, serializer.data)


class CustomUserSignupViewTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('customuser-signup')

    @patch('users.tasks.send_welcome_email.delay')
    def test_create_user_signup(self, mock_send_welcome_email):
        """Test signing up a new user"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'profile': {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'gender': 'F',
                'bio': 'Hello, I am Jane!',
                'phone': '1234567890',
                'town': 'Sample Town',
                'country': 'Sample Country'
            }
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that user was created properly
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpassword123'))
        self.assertEqual(user.profile.first_name, 'Jane')

        # Verify that the welcome email task was called
        mock_send_welcome_email.assert_called_once_with(user.id)

    def test_signup_password_mismatch(self):
        """Test signing up a user with mismatched passwords"""
        data = {
            'email': 'mismatch@example.com',
            'username': 'mismatchuser',
            'password': 'password123',
            'password2': 'differentpassword123',
        }
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Passwords do not match.")

