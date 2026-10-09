import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from social.models import Post


User = get_user_model()


class Wave1PostApiTests(APITestCase):
    base_url = "/api/v1/social/"

    def setUp(self):
        self.user = User.objects.create_user(
            email=f"post-{uuid.uuid4().hex[:8]}@example.com",
            username=f"post-user-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=self.user)

    def test_post_list_create_retrieve_patch_delete(self):
        create_payload = {
            "title": "Wave1 post",
            "content": "Initial content",
            "visibility": "public",
        }
        create_response = self.client.post(self.base_url, create_payload, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        post_id = create_response.data["id"]

        list_response = self.client.get(self.base_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        list_items = list_response.data if isinstance(list_response.data, list) else list_response.data.get("results", [])
        self.assertTrue(any(item["id"] == post_id for item in list_items))

        retrieve_response = self.client.get(f"{self.base_url}{post_id}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["id"], post_id)

        patch_response = self.client.patch(
            f"{self.base_url}{post_id}/",
            {"content": "Updated content"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["content"], "Updated content")

        delete_response = self.client.delete(f"{self.base_url}{post_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        deleted_post = Post.all_objects.get(id=post_id)
        self.assertTrue(deleted_post.is_deleted)

    def test_retrieve_nonexistent_post_returns_404(self):
        missing_id = uuid.uuid4()
        response = self.client.get(f"{self.base_url}{missing_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
