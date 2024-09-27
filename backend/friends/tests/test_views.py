# backend/friends/tests/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship
from django.core.exceptions import ValidationError

User = get_user_model()


class FriendRequestViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(
            email='sender@example.com',
            username='sender',
            password='password1'
        )
        self.receiver = User.objects.create_user(
            email='receiver@example.com',
            username='receiver',
            password='password2'
        )
        self.client.force_authenticate(user=self.sender)

    def test_send_friend_request(self):
        url = reverse('friendrequest-list')
        data = {'receiver': self.receiver.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.count(), 1)
        friend_request = FriendRequest.objects.first()
        self.assertEqual(friend_request.sender, self.sender)
        self.assertEqual(friend_request.receiver, self.receiver)

    def test_accept_friend_request(self):
        friend_request = FriendRequest.objects.create(sender=self.sender,
                                                      receiver=self.receiver)
        self.client.force_authenticate(user=self.receiver)
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'accepted')
        self.assertEqual(Friendship.objects.count(), 1)

    def test_cannot_accept_others_friend_request(self):
        friend_request = FriendRequest.objects.create(sender=self.sender,
                                                      receiver=self.receiver)
        other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='password3'
        )
        self.client.force_authenticate(user=other_user)
        url = reverse('friendrequest-detail', kwargs={'id': friend_request.id})
        data = {'status': 'accepted'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FriendshipViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2'
        )
        self.friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)
        self.client.force_authenticate(user=self.user1)

    def test_list_friendships(self):
        url = reverse('friendship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unfriend(self):
        url = reverse('friendship-detail', kwargs={'id': self.friendship.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_cannot_unfriend_if_not_involved(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='password3'
        )
        self.client.force_authenticate(user=other_user)
        url = reverse('friendship-detail', kwargs={'id': self.friendship.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
