import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from reactions.models import Reaction
from social.models import Post


User = get_user_model()


class Wave1ReactionsTests(APITestCase):
    base_url = "/api/v1/reactions/"

    def setUp(self):
        self.author = User.objects.create_user(
            email=f"react-author-{uuid.uuid4().hex[:8]}@example.com",
            username=f"react-author-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )
        self.reactor = User.objects.create_user(
            email=f"reactor-{uuid.uuid4().hex[:8]}@example.com",
            username=f"reactor-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )
        self.post = Post.objects.create(
            user=self.author,
            title="Reaction target",
            content="Target content",
            visibility="public",
        )
        self.payload = {
            "content_type": "post",
            "object_id": str(self.post.id),
            "emoji": "like",
        }

    def test_create_duplicate_remove_reaction(self):
        self.client.force_authenticate(user=self.reactor)

        create_response = self.client.post(self.base_url, self.payload, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reaction.objects.count(), 1)

        duplicate_response = self.client.post(self.base_url, self.payload, format="json")
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

        list_response = self.client.get(
            f"{self.base_url}?content_type=post&object_id={self.post.id}"
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        list_items = list_response.data if isinstance(list_response.data, list) else list_response.data.get("results", [])
        self.assertEqual(len(list_items), 1)

        remove_response = self.client.delete(
            f"{self.base_url}remove_reaction/",
            self.payload,
            format="json",
        )
        self.assertEqual(remove_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reaction.objects.count(), 0)

    def test_authentication_required_for_create(self):
        response = self.client.post(self.base_url, self.payload, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
