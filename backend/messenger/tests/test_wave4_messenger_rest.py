from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from messenger.models import Message

User = get_user_model()


class Wave4MessengerRestTests(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email='wave4-sender@example.com',
            username='wave4_sender',
            password='StrongPass123!',
        )
        self.receiver = User.objects.create_user(
            email='wave4-receiver@example.com',
            username='wave4_receiver',
            password='StrongPass123!',
        )
        self.other = User.objects.create_user(
            email='wave4-other@example.com',
            username='wave4_other',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=self.sender)

    def test_send_list_and_invalid_receiver(self):
        send_response = self.client.post(
            '/api/v1/messenger/',
            {'receiver': str(self.receiver.id), 'content': 'hello'},
            format='json',
        )
        self.assertEqual(send_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

        list_response = self.client.get('/api/v1/messenger/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data['count'], 1)

        invalid_receiver = self.client.post(
            '/api/v1/messenger/',
            {'receiver': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'content': 'nope'},
            format='json',
        )
        self.assertEqual(invalid_receiver.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipient_access_and_unauthorized_access_rejected(self):
        message = Message.objects.create(sender=self.sender, receiver=self.receiver, content='private')

        self.client.force_authenticate(user=self.receiver)
        recipient_retrieve = self.client.get(f'/api/v1/messenger/{message.id}/')
        self.assertEqual(recipient_retrieve.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.other)
        other_retrieve = self.client.get(f'/api/v1/messenger/{message.id}/')
        self.assertEqual(other_retrieve.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_as_read_and_sender_cannot_mark_receiver_message(self):
        message = Message.objects.create(sender=self.sender, receiver=self.receiver, content='mark me')

        self.client.force_authenticate(user=self.receiver)
        read_response = self.client.post(f'/api/v1/messenger/{message.id}/mark_as_read/')
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        message.refresh_from_db()
        self.assertTrue(message.is_read)

        second_read_response = self.client.post(f'/api/v1/messenger/{message.id}/mark_as_read/')
        self.assertEqual(second_read_response.status_code, status.HTTP_200_OK)

        message2 = Message.objects.create(sender=self.sender, receiver=self.receiver, content='no permission')
        self.client.force_authenticate(user=self.sender)
        forbidden = self.client.post(f'/api/v1/messenger/{message2.id}/mark_as_read/')
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
