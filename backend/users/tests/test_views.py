# users/tests/test_views.py

from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='Password@1234'  # Use a strong password to pass validators
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_current_user(self):
        url = reverse('users:customuser-me')  # Use namespaced URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'user@example.com')

    def test_update_current_user(self):
        url = reverse('users:customuser-me')  # Use namespaced URL
        data = {'email': 'newemail@example.com'}
        response = self.client.patch(url, data, format='json')  # Use PATCH for partial updates
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_retrieve_user(self):
        url = reverse('users:customuser-detail', kwargs={'pk': self.user.id})  # Use namespaced URL and 'pk'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'user@example.com')


class UserProfileViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='Password@1234'  # Use a strong password
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.profile = self.user.profile  # Retrieve the auto-created profile

    def test_retrieve_profile(self):
        url = reverse('users:userprofile-detail', kwargs={'pk': str(self.profile.id)})  # Use 'pk'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('first_name', ''), '')

    def test_update_profile(self):
        url = reverse('users:userprofile-detail', kwargs={'pk': str(self.profile.id)})  # Use 'pk'
        data = {'first_name': 'UpdatedName'}
        response = self.client.patch(url, data, format='json')  # Ensure format is 'json'
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'UpdatedName')


class CustomUserSignupViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup(self):
        url = reverse('users:customuser-signup')  # Use namespaced URL
        data = {
            'email': 'signupuser@example.com',
            'username': 'signupuser',
            'password': 'SecurePassword@1234',  # Use a strong password
            'password2': 'SecurePassword@1234',
            'profile': {
                'first_name': 'Signup',
                'last_name': 'User',
                'bio': 'I am new here.'
            }
        }
        response = self.client.post(url, data, format='json')  # Use 'json' format for nested data
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='signupuser@example.com').exists())
        # Optionally, verify profile creation
        signup_user = User.objects.get(email='signupuser@example.com')
        self.assertEqual(signup_user.profile.first_name, 'Signup')
        self.assertEqual(signup_user.profile.last_name, 'User')
        self.assertEqual(signup_user.profile.bio, 'I am new here.')

    def test_signup_password_mismatch(self):
        url = reverse('users:customuser-signup')  # Use namespaced URL
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'password': 'SecurePassword@1234',
            'password2': 'DifferentPassword@1234',  # Mismatched password
        }
        response = self.client.post(url, data, format='json')  # Use 'json' format
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(
            response.data['non_field_errors'][0],
            "Passwords do not match."
        )

    def test_signup_duplicate_email(self):
        # First signup
        url = reverse('users:customuser-signup')
        data = {
            'email': 'duplicate@example.com',
            'username': 'user1',
            'password': 'SecurePassword@1234',
            'password2': 'SecurePassword@1234',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Attempt to signup with the same email
        data = {
            'email': 'duplicate@example.com',
            'username': 'user2',
            'password': 'SecurePassword@1234',
            'password2': 'SecurePassword@1234',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        self.assertEqual(
            response.data['email'][0].code,
            'unique'
        )

    def test_signup_duplicate_username(self):
        # First signup
        url = reverse('users:customuser-signup')
        data = {
            'email': 'unique1@example.com',
            'username': 'duplicateuser',
            'password': 'SecurePassword@1234',
            'password2': 'SecurePassword@1234',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Attempt to signup with the same username
        data = {
            'email': 'unique2@example.com',
            'username': 'duplicateuser',
            'password': 'SecurePassword@1234',
            'password2': 'SecurePassword@1234',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
        self.assertEqual(
            response.data['username'][0].code,
            'unique'
        )

    def test_signup_missing_fields(self):
        url = reverse('users:customuser-signup')
        data = {
            'email': 'missingfields@example.com',
            # 'username' is missing
            'password': 'SecurePassword@1234',
            'password2': 'SecurePassword@1234',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
