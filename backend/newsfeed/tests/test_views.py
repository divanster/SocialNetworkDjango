from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story

User = get_user_model()


class UserFeedViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.client.force_authenticate(user=self.user)

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
        response = self.client.get('/api/newsfeed/')
        self.assertEqual(response.status_code, 200)

        # Check the aggregated feed data
        self.assertEqual(len(response.data['posts']), 1)
        self.assertEqual(response.data['posts'][0]['title'], 'Test Post')
        self.assertEqual(len(response.data['comments']), 1)
        self.assertEqual(response.data['comments'][0]['content'], 'Test Comment')
        self.assertEqual(len(response.data['reactions']), 1)
        self.assertEqual(response.data['reactions'][0]['type'], 'like')
        self.assertEqual(len(response.data['albums']), 1)
        self.assertEqual(response.data['albums'][0]['title'], 'Test Album')
        self.assertEqual(len(response.data['stories']), 1)
        self.assertEqual(response.data['stories'][0]['title'], 'Test Story')
