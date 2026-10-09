from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from friends.models import Block, FriendRequest, Friendship

User = get_user_model()


class Wave2DiscoveryTests(APITestCase):
    def setUp(self):
        self.current_user = User.objects.create_user(
            email='discover-me@example.com',
            username='discover_me',
            password='StrongPass123!',
        )
        self.friend_user = User.objects.create_user(
            email='discover-friend@example.com',
            username='friend_user',
            password='StrongPass123!',
        )
        self.blocked_user = User.objects.create_user(
            email='discover-blocked@example.com',
            username='blocked_user',
            password='StrongPass123!',
        )
        self.blocking_user = User.objects.create_user(
            email='discover-blocker@example.com',
            username='blocking_user',
            password='StrongPass123!',
        )
        self.pending_outgoing_user = User.objects.create_user(
            email='discover-outgoing@example.com',
            username='outgoing_user',
            password='StrongPass123!',
        )
        self.pending_incoming_user = User.objects.create_user(
            email='discover-incoming@example.com',
            username='incoming_user',
            password='StrongPass123!',
        )
        self.candidate_user = User.objects.create_user(
            email='discover-candidate@example.com',
            username='candidate_user',
            password='StrongPass123!',
        )

        user1, user2 = sorted([self.current_user, self.friend_user], key=lambda user: str(user.id))
        Friendship.objects.create(user1=user1, user2=user2)
        Block.objects.create(blocker=self.current_user, blocked=self.blocked_user)
        Block.objects.create(blocker=self.blocking_user, blocked=self.current_user)
        FriendRequest.objects.create(sender=self.current_user, receiver=self.pending_outgoing_user)
        FriendRequest.objects.create(sender=self.pending_incoming_user, receiver=self.current_user)

        self.client.force_authenticate(user=self.current_user)

    def test_suggestions_exclusions_and_inclusion(self):
        response = self.client.get('/api/v1/users/suggestions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item['username'] for item in response.data}
        self.assertNotIn(self.current_user.username, usernames)
        self.assertNotIn(self.friend_user.username, usernames)
        self.assertNotIn(self.blocked_user.username, usernames)
        self.assertNotIn(self.blocking_user.username, usernames)
        self.assertNotIn(self.pending_outgoing_user.username, usernames)
        self.assertNotIn(self.pending_incoming_user.username, usernames)
        self.assertIn(self.candidate_user.username, usernames)

    def test_search_matching_nonmatching_and_empty_query(self):
        match_response = self.client.get('/api/v1/search/', {'query': 'candidate'})
        self.assertEqual(match_response.status_code, status.HTTP_200_OK)
        usernames = {item['username'] for item in match_response.data['users']}
        self.assertIn(self.candidate_user.username, usernames)
        self.assertNotIn(self.friend_user.username, usernames)

        nonmatch_response = self.client.get('/api/v1/search/', {'query': 'no_such_user_123'})
        self.assertEqual(nonmatch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(nonmatch_response.data['users'], [])

        empty_response = self.client.get('/api/v1/search/', {'query': ''})
        self.assertEqual(empty_response.status_code, status.HTTP_200_OK)
        self.assertEqual(empty_response.data, {'users': [], 'posts': [], 'albums': [], 'stories': []})

    def test_search_excludes_blocked_users(self):
        response = self.client.get('/api/v1/search/', {'query': 'blocked'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item['username'] for item in response.data['users']}
        self.assertNotIn(self.blocked_user.username, usernames)

    def test_discovery_requires_authentication(self):
        self.client.force_authenticate(user=None)
        suggestions_response = self.client.get('/api/v1/users/suggestions/')
        search_response = self.client.get('/api/v1/search/', {'query': 'candidate'})
        self.assertEqual(suggestions_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(search_response.status_code, status.HTTP_401_UNAUTHORIZED)
