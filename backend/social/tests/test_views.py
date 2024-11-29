from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from social.models import Post
from friends.models import Friendship
from core.choices import VisibilityChoices
from rest_framework_simplejwt.tokens import RefreshToken  # Use simplejwt for JWT token

User = get_user_model()

class AggregatedFeedViewTest(APITestCase):

    def setUp(self):
        # Create a test user with email (required by custom user manager)
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required field in your user model
            password='password'
        )

        # Generate JWT token for the user using SimpleJWT
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Authenticate the user using JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)  # Using JWT Bearer token

        # Create another user for testing
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',  # Required field in your user model
            password='password'
        )

        # Create a post by the user
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post',
            author=self.user,
            visibility=VisibilityChoices.PUBLIC
        )

        # Create a post by another user (for testing friend's visibility)
        self.friend_post = Post.objects.create(
            title='Friend Post',
            content='This is a post by a friend',
            author=self.other_user,
            visibility=VisibilityChoices.FRIENDS
        )

        # Create a friendship for testing visibility for 'friends' posts
        Friendship.objects.create(user1=self.user, user2=self.other_user)

        # Set up the URL for the aggregated feed view
        self.url = reverse('newsfeed:user_feed')  # Corrected URL name to match your urlpatterns

    def test_aggregated_feed_authenticated(self):
        # Send the GET request to the aggregated feed view
        response = self.client.get(self.url)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains posts and other expected fields
        self.assertIn('posts', response.data)
        self.assertGreater(len(response.data['posts']), 0)

        # Verify that the public post is in the feed
        post_titles = [post['title'] for post in response.data['posts']]
        self.assertIn('Test Post', post_titles)  # The post created by testuser
        self.assertIn('Friend Post', post_titles)  # The post created by otheruser (visible to friends)

    def test_aggregated_feed_no_posts(self):
        # Create a new user without posts
        user_without_posts = User.objects.create_user(
            username='emptyuser',
            email='emptyuser@example.com',  # Required field
            password='password'
        )

        # Generate JWT token for the new user
        refresh = RefreshToken.for_user(user_without_posts)
        self.token = str(refresh.access_token)

        # Authenticate the new user using JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Send the GET request to the aggregated feed view
        response = self.client.get(self.url)

        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response does not contain posts
        self.assertIn('posts', response.data)
        self.assertEqual(len(response.data['posts']), 0)

    def test_aggregated_feed_unauthenticated(self):
        # Send a GET request without authentication
        self.client.credentials()  # Clear any authentication credentials
        response = self.client.get(self.url)

        # Check if the response is unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_aggregated_feed_friends_visibility(self):
        # Send the GET request to the aggregated feed view
        response = self.client.get(self.url)

        # Check that the friend post is visible to the authenticated user
        post_titles = [post['title'] for post in response.data.get('posts', [])]  # Avoid KeyError
        self.assertIn('Friend Post', post_titles)  # The post by a friend should be included

    def test_aggregated_feed_other_user_post_not_visible(self):
        # Create another user without adding as a friend
        user_not_a_friend = User.objects.create_user(
            username='notafriend',
            email='notafriend@example.com',  # Required field
            password='password'
        )

        # Generate JWT token for the new user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Authenticate the user using JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Send the GET request to the aggregated feed view
        response = self.client.get(self.url)

        # Ensure that the friend's post is not included (as they're not friends)
        post_titles = [post['title'] for post in response.data.get('posts', [])]  # Avoid KeyError
        self.assertNotIn('Friend Post', post_titles)  # The post by another user should not appear
