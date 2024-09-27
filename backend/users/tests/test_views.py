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
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_current_user(self):
        # Use the correct name and namespace 'users:customuser-me'
        url = reverse('users:customuser-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'user@example.com')

    def test_update_current_user(self):
        # Use the correct name and namespace 'users:customuser-me'
        url = reverse('users:customuser-me')
        data = {'email': 'newemail@example.com'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_retrieve_user(self):
        # Use the correct name and namespace 'users:customuser-detail'
        url = reverse('users:customuser-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'user@example.com')

class UserProfileViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='password123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        # Use the correct name and namespace 'users:userprofile-detail'
        url = reverse('users:userprofile-detail', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], '')

    def test_update_profile(self):
        # Use the correct name and namespace 'users:userprofile-detail'
        url = reverse('users:userprofile-detail', kwargs={'pk': self.profile.id})
        data = {'first_name': 'UpdatedName'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'UpdatedName')

class CustomUserSignupViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup(self):
        # Use the correct name and namespace 'users:user-signup'
        url = reverse('users:user-signup')
        data = {
            'email': 'signupuser@example.com',
            'username': 'signupuser',
            'password': 'password123',
            'confirm_password': 'password123',
            'profile': {
                'first_name': 'Signup',
                'last_name': 'User',
                'bio': 'I am new here.'
            }
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='signupuser@example.com').exists())

    def test_signup_password_mismatch(self):
        # Use the correct name and namespace 'users:user-signup'
        url = reverse('users:user-signup')
        data = {
            'email': 'user@example.com',
            'username': 'user',
            'password': 'password123',
            'confirm_password': 'password456',  # Mismatched password
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(
            response.data['non_field_errors'][0],
            "Passwords do not match."
        )
