from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from reactions.models import Reaction
from django.urls import reverse

User = get_user_model()


class ReactionViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser",
                                             password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.reaction_data = {
            "reacted_item_type": "Post",
            "reacted_item_id": "1",
            "emoji": "like",
        }

    def test_create_reaction(self):
        url = reverse('reaction-list')
        response = self.client.post(url, self.reaction_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 1)

    def test_get_reactions(self):
        Reaction.objects.create(user_id=self.user.id, user_username=self.user.username,
                                **self.reaction_data)
        url = reverse('reaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_reaction(self):
        reaction = Reaction.objects.create(user_id=self.user.id,
                                           user_username=self.user.username,
                                           **self.reaction_data)
        url = reverse('reaction-detail', args=[reaction.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reaction.objects.count(), 0)
