# backend/comments/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from comments.models import Comment
from social.models import Post
from django.contrib.auth import get_user_model

# Getting the User model
User = get_user_model()


class CommentModelTestCase(TestCase):
    """
    Test case for validating the behavior of the Comment model.
    - This includes testing comment creation, string representation,
      missing content validation, and reverse relationship with the Post.
    """

    def setUp(self):
        """
        Set up the initial data for tests:
        - Create a user and a post to associate comments with.
        """
        # Creating a test user
        self.user = User.objects.create_user(email='user@example.com',
                                             username='testuser',
                                             password='password123')
        # Creating a test post associated with the user
        self.post = Post.objects.create(author=self.user, title='Test Post',
                                        content='Test Post Content')

    def test_create_comment(self):
        """
        Test the creation of a Comment instance.
        - Check if the comment count is accurate after creation.
        - Ensure that attributes such as content, user, and post are correctly set.
        """
        # Creating a comment
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='Test Comment Content')

        # Validating creation of comment
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.content, 'Test Comment Content')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)

    def test_str_method(self):
        """
        Test the `__str__()` method of the Comment model.
        - The string representation should be a truncated version of the comment content.
        """
        # Creating a long comment to test truncation
        comment = Comment.objects.create(user=self.user, post=self.post,
                                         content='A long comment that should be truncated.')
        # Verifying the `__str__()` output of the comment
        self.assertEqual(str(comment), 'A long comment that sho')

    def test_create_comment_without_content(self):
        """
        Test the creation of a comment without content.
        - Should raise `ValidationError`.
        """
        # Testing creation of a comment without content to ensure it raises `ValidationError`
        with self.assertRaises(ValidationError):
            comment = Comment(user=self.user, post=self.post, content='')
            # Triggering the validation manually using `full_clean()`
            comment.full_clean()

    def test_related_post_comments(self):
        """
        Test the reverse relationship between Post and Comment.
        - Ensure that comments are properly linked to the post using the `post.comments` manager.
        """
        # Creating multiple comments for the post
        comment1 = Comment.objects.create(user=self.user, post=self.post,
                                          content='Comment 1')
        comment2 = Comment.objects.create(user=self.user, post=self.post,
                                          content='Comment 2')

        # Validating the number of comments associated with the post
        self.assertEqual(self.post.comments.count(), 2)

        # Ensuring that both comments are present in the post's related comments
        self.assertIn(comment1, self.post.comments.all())
        self.assertIn(comment2, self.post.comments.all())

    def tearDown(self):
        """
        Cleanup after each test.
        - Deleting all comments, posts, and users.
        """
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.all().delete()
