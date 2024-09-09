# tests/test_views.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from friends.models import FriendRequest, Friendship
from django.contrib.auth import get_user_model

User = get_user_model()


class FriendRequestViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create two users
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.friend_request_url = reverse(
            'friendrequest-list')  # Assuming you're using a router for FriendRequestViewSet

    def test_create_friend_request(self):
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Send a POST request to create a friend request
        response = self.client.post(self.friend_request_url,
                                    {'receiver': self.user2.id})

        # Check that the response status is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the friend request was created
        self.assertEqual(FriendRequest.objects.count(), 1)
        friend_request = FriendRequest.objects.first()
        self.assertEqual(friend_request.sender, self.user1)
        self.assertEqual(friend_request.receiver, self.user2)
        self.assertEqual(friend_request.status, 'pending')

    def test_accept_friend_request(self):
        # Create a friend request
        friend_request = FriendRequest.objects.create(sender=self.user1,
                                                      receiver=self.user2)

        # Authenticate user2 (the receiver)
        self.client.force_authenticate(user=self.user2)

        # Send a PUT request to accept the friend request
        url = reverse('friendrequest-detail', args=[friend_request.id])
        response = self.client.put(url, {'status': 'accepted'})

        # Check the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the status is updated
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'accepted')

        # Check that the friendship was created
        self.assertEqual(Friendship.objects.count(), 1)
        friendship = Friendship.objects.first()
        self.assertEqual(friendship.user1, self.user1)
        self.assertEqual(friendship.user2, self.user2)


class FriendshipViewSetTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create two users and a friendship
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)
        self.friendship_url = reverse(
            'friendship-list')  # Assuming you're using a router for FriendshipViewSet

    def test_list_friendships(self):
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Send a GET request to list friendships
        response = self.client.get(self.friendship_url)

        # Check the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the data returned contains the friendship
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user1'], self.user1.id)
        self.assertEqual(response.data[0]['user2'], self.user2.id)

    def test_unfriend(self):
        # Authenticate user1
        self.client.force_authenticate(user=self.user1)

        # Send a DELETE request to unfriend user2
        url = reverse('friendship-detail', args=[self.friendship.id])
        response = self.client.delete(url)

        # Check the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the friendship is deleted
        self.assertEqual(Friendship.objects.count(), 0)
