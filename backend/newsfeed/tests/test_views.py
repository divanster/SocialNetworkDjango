from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story

User = get_user_model()


class UserFeedViewTest(APITestCase):
    def setUp(self):
        # Set up the API client and authenticate user
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.client.force_authenticate(user=self.user)

        # Create test data for posts, comments, reactions, albums, and stories
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Some content')
        self.comment = Comment.objects.create(user=self.user, post=self.post,
                                              content='Test Comment')
        self.reaction = Reaction.objects.create(user=self.user, post=self.post,
                                                type='like')
        self.album = Album.objects.create(user=self.user, title='Test Album',
                                          description='Test Description')
        self.story = Story.objects.create(user=self.user, title='Test Story',
                                          content='Test Story Content')

    def test_get_user_feed(self):
        # Get the URL using the reverse function
        url = reverse('newsfeed:user-feed')

        # Make a GET request to the endpoint
        response = self.client.get(url)

        # Ensure that the response returns a status code of 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "User feed did not return a 200 status code.")

        # Check the aggregated feed data
        self.assertIn('posts', response.data,
                      "The response does not contain 'posts' key.")
        self.assertEqual(len(response.data['posts']), 1,
                         "There should be 1 post in the response data.")
        self.assertEqual(response.data['posts'][0]['title'], 'Test Post',
                         "The post title does not match the expected value.")

        self.assertIn('comments', response.data,
                      "The response does not contain 'comments' key.")
        self.assertEqual(len(response.data['comments']), 1,
                         "There should be 1 comment in the response data.")
        self.assertEqual(response.data['comments'][0]['content'], 'Test Comment',
                         "The comment content does not match the expected value.")

        self.assertIn('reactions', response.data,
                      "The response does not contain 'reactions' key.")
        self.assertEqual(len(response.data['reactions']), 1,
                         "There should be 1 reaction in the response data.")
        self.assertEqual(response.data['reactions'][0]['type'], 'like',
                         "The reaction type does not match the expected value.")

        self.assertIn('albums', response.data,
                      "The response does not contain 'albums' key.")
        self.assertEqual(len(response.data['albums']), 1,
                         "There should be 1 album in the response data.")
        self.assertEqual(response.data['albums'][0]['title'], 'Test Album',
                         "The album title does not match the expected value.")

        self.assertIn('stories', response.data,
                      "The response does not contain 'stories' key.")
        self.assertEqual(len(response.data['stories']), 1,
                         "There should be 1 story in the response data.")
        self.assertEqual(response.data['stories'][0]['title'], 'Test Story',
                         "The story title does not match the expected value.")

    def test_get_user_feed_no_data(self):
        # Remove all existing data to test empty response
        Post.objects.all().delete()
        Comment.objects.all().delete()
        Reaction.objects.all().delete()
        Album.objects.all().delete()
        Story.objects.all().delete()

        # Get the URL using the reverse function
        url = reverse('newsfeed:user-feed')

        # Make a GET request to the endpoint
        response = self.client.get(url)

        # Ensure that the response returns a status code of 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "User feed did not return a 200 status code with no data.")

        # Ensure that the response contains empty lists for each feed component
        self.assertEqual(len(response.data['posts']), 0,
                         "The response should contain 0 posts.")
        self.assertEqual(len(response.data['comments']), 0,
                         "The response should contain 0 comments.")
        self.assertEqual(len(response.data['reactions']), 0,
                         "The response should contain 0 reactions.")
        self.assertEqual(len(response.data['albums']), 0,
                         "The response should contain 0 albums.")
        self.assertEqual(len(response.data['stories']), 0,
                         "The response should contain 0 stories.")

