from django.test import TestCase
from social.models import Post, PostImage, Rating
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post content.",
            author=self.user,
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.content, "This is a test post content.")
        self.assertEqual(self.post.author.username, "testuser")

    def test_post_str_method(self):
        self.assertEqual(str(self.post), "Test Post")

    def test_average_rating_no_ratings(self):
        self.assertEqual(self.post.average_rating, 0)

    def test_average_rating_with_ratings(self):
        Rating.objects.create(post=self.post, user=self.user, value=4)
        # Create a rating with a different user to avoid duplication
        another_user = User.objects.create_user(username="anotheruser", email="anotheruser@example.com", password="password")
        Rating.objects.create(post=self.post, user=another_user, value=5)
        self.assertEqual(self.post.average_rating, 4.5)

    def test_average_rating_with_edge_case(self):
        Rating.objects.create(post=self.post, user=self.user, value=1)
        # Create a rating with a different user to avoid duplication
        another_user = User.objects.create_user(username="anotheruser", email="anotheruser@example.com", password="password")
        Rating.objects.create(post=self.post, user=another_user, value=5)
        expected_avg = (1 + 5) / 2
        self.assertEqual(self.post.average_rating, expected_avg)

class PostImageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.post = Post.objects.create(
            title="Test Post for Image",
            content="Content for image.",
            author=self.user
        )

    def test_post_image_creation(self):
        post_image = PostImage.objects.create(post=self.post, image="path/to/test_image.jpg")
        self.assertEqual(post_image.post, self.post)
        self.assertEqual(post_image.image.name, "path/to/test_image.jpg")

    def test_post_image_str_method(self):
        post_image = PostImage.objects.create(post=self.post, image="path/to/test_image.jpg")
        self.assertEqual(str(post_image), f"Image for Post '{self.post.title}'")

class RatingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.post = Post.objects.create(
            title="Test Post for Rating",
            content="Content for rating.",
            author=self.user
        )

    def test_rating_creation(self):
        rating = Rating.objects.create(post=self.post, user=self.user, value=4)
        self.assertEqual(rating.post, self.post)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.value, 4)

    def test_rating_str_method(self):
        rating = Rating.objects.create(post=self.post, user=self.user, value=4)
        self.assertEqual(str(rating), f"Rating 4 Stars by User '{self.user.username}'")

    def test_rating_validation(self):
        invalid_rating = Rating(post=self.post, user=self.user, value=6)
        with self.assertRaises(ValidationError):
            invalid_rating.clean()  # Ensure clean method is called to validate

    def test_rating_unique_constraint(self):
        Rating.objects.create(post=self.post, user=self.user, value=4)
        duplicate_rating = Rating(post=self.post, user=self.user, value=5)
        with self.assertRaises(ValidationError):
            duplicate_rating.full_clean()
