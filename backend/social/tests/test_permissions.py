from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from core.permissions import IsAuthorOrReadOnly
from social.models import Post

User = get_user_model()


class MockView(APIView):
    # A mock view to test permissions
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get(self, request):
        return Response({"message": "GET request successful"})

    def post(self, request):
        return Response({"message": "POST request successful"}, status=status.HTTP_201_CREATED)

    def put(self, request):
        return Response({"message": "PUT request successful"})

    def delete(self, request):
        return Response({"message": "DELETE request successful"})


class IsAuthorOrReadOnlyTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # Create two users
        self.author = User.objects.create_user(
            username='author', email='author@example.com', password='password123')
        self.other_user = User.objects.create_user(
            username='other_user', email='other_user@example.com', password='password123')

        # Create a post
        self.post = Post.objects.create(
            title="Test Post",
            content="Test Content",
            author_id=self.author.id,
            author_username=self.author.username,
        )

        # Mock view instance
        self.view = MockView.as_view()

    def test_get_request_allows_anyone(self):
        # GET requests should be allowed for any user
        request = self.factory.get('/posts/')
        request.user = self.other_user

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "GET request successful")

    def test_head_request_allows_anyone(self):
        # HEAD requests should be allowed for any user
        request = self.factory.head('/posts/')
        request.user = self.other_user

        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_options_request_allows_anyone(self):
        # OPTIONS requests should be allowed for any user
        request = self.factory.options('/posts/')
        request.user = self.other_user

        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_post_request_not_allowed_for_non_author(self):
        # POST requests should not be allowed for a non-author (without ownership check)
        request = self.factory.post('/posts/')
        request.user = self.other_user

        with self.assertRaises(PermissionDenied):
            self.view(request)

    def test_put_request_allowed_for_author(self):
        # PUT requests should be allowed only for the author
        request = self.factory.put('/posts/')
        request.user = self.author

        # Attach the post to the view's kwargs for testing permissions
        response = self.view(request, pk=self.post.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "PUT request successful")

    def test_put_request_denied_for_non_author(self):
        # PUT requests should be denied for a user who is not the author
        request = self.factory.put('/posts/')
        request.user = self.other_user

        with self.assertRaises(PermissionDenied):
            self.view(request, pk=self.post.id)

    def test_delete_request_allowed_for_author(self):
        # DELETE requests should be allowed only for the author
        request = self.factory.delete('/posts/')
        request.user = self.author

        # Attach the post to the view's kwargs for testing permissions
        response = self.view(request, pk=self.post.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "DELETE request successful")

    def test_delete_request_denied_for_non_author(self):
        # DELETE requests should be denied for a user who is not the author
        request = self.factory.delete('/posts/')
        request.user = self.other_user

        with self.assertRaises(PermissionDenied):
            self.view(request, pk=self.post.id)

    def test_author_access_post_request(self):
        # POST request by author (ownership assumed here for creation)
        request = self.factory.post('/posts/')
        request.user = self.author

        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], "POST request successful")
