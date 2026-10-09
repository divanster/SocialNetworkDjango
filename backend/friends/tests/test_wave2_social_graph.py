from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from friends.models import Block, FriendRequest, Friendship

User = get_user_model()


class Wave2FriendGraphTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email='a@example.com', username='user_a', password='StrongPass123!')
        self.user_b = User.objects.create_user(email='b@example.com', username='user_b', password='StrongPass123!')
        self.user_c = User.objects.create_user(email='c@example.com', username='user_c', password='StrongPass123!')
        self.client.force_authenticate(user=self.user_a)

    def test_send_friend_request_success(self):
        response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.filter(sender=self.user_a, receiver=self.user_b).count(), 1)

    def test_send_friend_request_duplicate_rejected(self):
        FriendRequest.objects.create(sender=self.user_a, receiver=self.user_b)
        response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_friend_request_to_self_rejected(self):
        response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_a.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reverse_pending_request_rejected(self):
        FriendRequest.objects.create(sender=self.user_b, receiver=self.user_a)
        response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_friend_request_creates_friendship(self):
        friend_request = FriendRequest.objects.create(sender=self.user_b, receiver=self.user_a)
        response = self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Friendship.objects.filter(
                user1__in=[self.user_a, self.user_b],
                user2__in=[self.user_a, self.user_b]
            ).exists()
        )

    def test_reject_friend_request(self):
        friend_request = FriendRequest.objects.create(sender=self.user_b, receiver=self.user_a)
        response = self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, FriendRequest.Status.REJECTED)

    def test_sender_cannot_accept_or_reject(self):
        friend_request = FriendRequest.objects.create(sender=self.user_a, receiver=self.user_b)
        accept_response = self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/accept/')
        reject_response = self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/reject/')
        self.assertEqual(accept_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(reject_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_existing_friendship_blocks_new_request(self):
        user1, user2 = sorted([self.user_a, self.user_b], key=lambda u: str(u.id))
        Friendship.objects.create(user1=user1, user2=user2)
        response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_b.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_friendships_list_and_remove(self):
        friend_request = FriendRequest.objects.create(sender=self.user_b, receiver=self.user_a)
        self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/accept/')
        list_response = self.client.get('/api/v1/friends/friendships/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 1)
        friendship_id = list_response.data['results'][0]['id']
        self.assertIn('full_name', list_response.data['results'][0]['user1'])
        delete_response = self.client.delete(f'/api/v1/friends/friendships/{friendship_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_block_create_duplicate_self_remove_list(self):
        create_response = self.client.post('/api/v1/friends/blocks/', {'blocked_id': str(self.user_b.id)}, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        duplicate_response = self.client.post('/api/v1/friends/blocks/', {'blocked_id': str(self.user_b.id)}, format='json')
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self_block_response = self.client.post('/api/v1/friends/blocks/', {'blocked_id': str(self.user_a.id)}, format='json')
        self.assertEqual(self_block_response.status_code, status.HTTP_400_BAD_REQUEST)
        list_response = self.client.get('/api/v1/friends/blocks/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 1)
        block_id = list_response.data['results'][0]['id']
        delete_response = self.client.delete(f'/api/v1/friends/blocks/{block_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_cannot_send_or_accept(self):
        friend_request = FriendRequest.objects.create(sender=self.user_b, receiver=self.user_a)
        self.client.force_authenticate(user=None)
        create_response = self.client.post('/api/v1/friends/friend-requests/', {'receiver_id': str(self.user_c.id)}, format='json')
        accept_response = self.client.post(f'/api/v1/friends/friend-requests/{friend_request.id}/accept/')
        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(accept_response.status_code, status.HTTP_401_UNAUTHORIZED)
