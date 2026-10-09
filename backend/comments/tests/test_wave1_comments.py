import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from comments.models import Comment
from social.models import Post


User = get_user_model()


class Wave1CommentsTests(APITestCase):
    base_url = "/api/v1/comments/comments/"

    def setUp(self):
        self.author = User.objects.create_user(
            email=f"author-{uuid.uuid4().hex[:8]}@example.com",
            username=f"author-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email=f"other-{uuid.uuid4().hex[:8]}@example.com",
            username=f"other-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )
        self.post = Post.objects.create(
            user=self.author,
            title="Comment target",
            content="Target body",
            visibility="public",
        )

    def test_create_list_edit_delete_own_comment(self):
        self.client.force_authenticate(user=self.author)
        create_response = self.client.post(
            self.base_url,
            {"post_id": str(self.post.id), "content": "My comment"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        comment_id = create_response.data["id"]

        list_response = self.client.get(f"{self.base_url}?post_id={self.post.id}")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        list_items = list_response.data if isinstance(list_response.data, list) else list_response.data.get("results", [])
        self.assertTrue(any(item["id"] == comment_id for item in list_items))

        patch_response = self.client.patch(
            f"{self.base_url}{comment_id}/",
            {"content": "Edited comment"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data["content"], "Edited comment")

        delete_response = self.client.delete(f"{self.base_url}{comment_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_reject_unauthorized_edit(self):
        self.client.force_authenticate(user=self.author)
        comment = self.client.post(
            self.base_url,
            {"post_id": str(self.post.id), "content": "Owner comment"},
            format="json",
        ).data

        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"{self.base_url}{comment['id']}/",
            {"content": "Hacked edit"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_target_returns_4xx(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.post(
            self.base_url,
            {"post_id": str(uuid.uuid4()), "content": "Invalid target"},
            format="json",
        )
        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)

    def test_authentication_required_for_create(self):
        response = self.client.post(
            self.base_url,
            {"post_id": str(self.post.id), "content": "No auth"},
            format="json",
        )
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
