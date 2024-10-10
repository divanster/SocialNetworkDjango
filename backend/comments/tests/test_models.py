# backend/comments/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from comments.models import Comment
from social.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Test Post Content')

    def test_create_comment(self):
        # Test creation of a comment
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Test Comment Content')
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.content, 'Test Comment Content')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)

    def test_str_method(self):
        # Test the __str__ method of the Comment model
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='A long comment that should be truncated.')
        self.assertEqual(str(comment), 'A long comment that sho')

    def test_create_comment_without_content(self):
        # Test comment creation without content, should raise ValidationError
        with self.assertRaises(ValidationError):
            comment = Comment(user=self.user, post=self.post, content='')
            comment.full_clean()  # This is used to manually trigger the model validation

    def test_related_post_comments(self):
        # Test post's related comments
        comment1 = Comment.objects.create(user=self.user, post=self.post,
                                          content='Comment 1')
        comment2 = Comment.objects.create(user=self.user, post=self.post,
                                          content='Comment 2')

        self.assertEqual(self.post.comments.count(), 2)
        self.assertIn(comment1, self.post.comments.all())
        self.assertIn(comment2, self.post.comments.all())
