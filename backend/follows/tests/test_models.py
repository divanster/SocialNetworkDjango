from django.test import TestCase
from django.contrib.auth import get_user_model
from follows.models import Follow

User = get_user_model()


class FollowModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com',
                                              username='user1', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com',
                                              username='user2', password='password123')

    def test_create_follow(self):
        # Test creation of a follow
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.followed, self.user2)

    def test_str_method(self):
        # Test the __str__ method
        follow = Follow.objects.create(follower=self.user1, followed=self.user2)
        self.assertEqual(str(follow), "user1 follows user2")
