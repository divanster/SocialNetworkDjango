# users/tests/test_serializers.py
from django.test import TestCase
from users.models import CustomUser
from users.serializers import CustomUserSerializer

class CustomUserSerializerTests(TestCase):

    def test_user_serializer(self):
        """Test the user serializer"""
        user = CustomUser.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        serializer = UserSerializer(user)

        self.assertEqual(serializer.data['email'], user.email)
        self.assertEqual(serializer.data['username'], user.username)
