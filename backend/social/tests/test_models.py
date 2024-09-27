# backend/social/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from social.models import Post, PostImage, Rating, Tag
from django.core.exceptions import ValidationError

User = get_user_model()


class PostModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )

    def test_create_post(self):
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user
        )
        self.assertEqual(str(post), 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, 'This is a test post.')
        self.assertEqual(post.average_rating, 0)

    def test_average_rating(self):
        post = Post.objects.create(
            title='Rated Post',
            content='This post will be rated.',
            author=self.user
        )
        Rating.objects.create(post=post, user=self.user, value=4)
        another_user = User.objects.create_user(
            email='anotheruser@example.com',
            username='anotheruser',
            password='anotherpassword'
        )
        Rating.objects.create(post=post, user=another_user, value=2)
        self.assertEqual(post.average_rating, 3)  # (4 + 2) / 2


class PostImageModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='imageuser@example.com',
            username='imageuser',
            password='imagepassword'
        )
        self.post = Post.objects.create(
            title='Image Post',
            content='Post with images.',
            author=self.user
        )

    def test_create_post_image(self):
        # Since ImageField requires an actual file, we use SimpleUploadedFile
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile('test_image.jpg', b'file_content',
                                   content_type='image/jpeg')
        post_image = PostImage.objects.create(post=self.post, image=image)
        self.assertEqual(str(post_image), 'Image Post Image')
        self.assertEqual(post_image.post, self.post)


class RatingModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='ratinguser@example.com',
            username='ratinguser',
            password='ratingpassword'
        )
        self.post = Post.objects.create(
            title='Rating Post',
            content='Post to be rated.',
            author=self.user
        )

    def test_create_valid_rating(self):
        rating = Rating.objects.create(post=self.post, user=self.user, value=5)
        self.assertEqual(str(rating), 'Rating Post - 5 Stars')
        self.assertEqual(rating.value, 5)

    def test_create_invalid_rating(self):
        with self.assertRaises(ValidationError):
            rating = Rating(post=self.post, user=self.user, value=6)
            rating.clean()  # Triggers the validation

    def test_unique_together_constraint(self):
        Rating.objects.create(post=self.post, user=self.user, value=4)
        with self.assertRaises(Exception):
            # Should raise an IntegrityError or ValidationError
            Rating.objects.create(post=self.post, user=self.user, value=3)


class TagModelTests(TestCase):

    def test_create_tag(self):
        tag = Tag.objects.create(name='Test Tag')
        self.assertEqual(str(tag), 'Test Tag')
