from django.test import TestCase
from social.models import Post, PostImage, Rating
from django.core.exceptions import ValidationError


class PostModelTest(TestCase):

    def setUp(self):
        # Set up a test post for use in multiple test cases
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post content.",
            author_id=1,
            author_username="testuser"
        )

    def test_post_creation(self):
        # Test that the post instance is created correctly
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.content, "This is a test post content.")
        self.assertEqual(self.post.author_id, 1)
        self.assertEqual(self.post.author_username, "testuser")

    def test_post_str_method(self):
        # Test that the string representation of the post is as expected
        self.assertEqual(str(self.post), "Test Post")

    def test_average_rating_no_ratings(self):
        # Test that the average rating is 0 if no ratings exist
        self.assertEqual(self.post.average_rating, 0)

    def test_average_rating_with_ratings(self):
        # Add some ratings and test the average
        Rating.objects.create(post_id=self.post.id, user_id=2, user_username="user2", value=4)
        Rating.objects.create(post_id=self.post.id, user_id=3, user_username="user3", value=5)

        self.assertEqual(self.post.average_rating, 4.5)

    def test_average_rating_with_ratings_edge_cases(self):
        # Add ratings with edge values (1 and 5)
        Rating.objects.create(post_id=self.post.id, user_id=4, user_username="user4", value=1)
        Rating.objects.create(post_id=self.post.id, user_id=5, user_username="user5", value=5)

        expected_average = (4 + 5 + 1 + 5) / 4
        self.assertAlmostEqual(self.post.average_rating, expected_average)


class PostImageModelTest(TestCase):

    def setUp(self):
        # Set up a test post for associating images
        self.post = Post.objects.create(
            title="Test Post for Image",
            content="This is a test post content for image.",
            author_id=1,
            author_username="testuser"
        )

    def test_post_image_creation(self):
        # Test that a post image is created correctly
        post_image = PostImage.objects.create(
            post_id=self.post.id,
            image="path/to/test_image.jpg"
        )

        self.assertEqual(post_image.post_id, str(self.post.id))
        self.assertEqual(post_image.image.name, "path/to/test_image.jpg")

    def test_post_image_str_method(self):
        # Test the string representation of the post image
        post_image = PostImage.objects.create(
            post_id=self.post.id,
            image="path/to/test_image.jpg"
        )
        expected_str = f"Image for Post ID {self.post.id}"
        self.assertEqual(str(post_image), expected_str)


class RatingModelTest(TestCase):

    def setUp(self):
        # Set up a test post for rating
        self.post = Post.objects.create(
            title="Test Post for Rating",
            content="This is a test post content for rating.",
            author_id=1,
            author_username="testuser"
        )

    def test_rating_creation(self):
        # Test that a rating is created correctly
        rating = Rating.objects.create(
            post_id=self.post.id,
            user_id=1,
            user_username="testuser",
            value=4
        )

        self.assertEqual(rating.post_id, str(self.post.id))
        self.assertEqual(rating.user_id, 1)
        self.assertEqual(rating.user_username, "testuser")
        self.assertEqual(rating.value, 4)

    def test_rating_str_method(self):
        # Test the string representation of the rating
        rating = Rating.objects.create(
            post_id=self.post.id,
            user_id=1,
            user_username="testuser",
            value=4
        )
        expected_str = f"Rating 4 Stars for Post ID {self.post.id}"
        self.assertEqual(str(rating), expected_str)

    def test_rating_validation(self):
        # Test that rating validation enforces value between 1 and 5
        rating = Rating(
            post_id=self.post.id,
            user_id=1,
            user_username="testuser",
            value=6
        )
        with self.assertRaises(ValidationError):
            rating.clean()  # This should raise a ValidationError

        rating.value = 0
        with self.assertRaises(ValidationError):
            rating.clean()  # This should also raise a ValidationError

    def test_rating_unique_constraint(self):
        # Test that a user can only rate a post once
        Rating.objects.create(
            post_id=self.post.id,
            user_id=1,
            user_username="testuser",
            value=4
        )

        # Attempt to create another rating by the same user for the same post
        duplicate_rating = Rating(
            post_id=self.post.id,
            user_id=1,
            user_username="testuser",
            value=3
        )
        with self.assertRaises(ValidationError):
            duplicate_rating.full_clean()  # This should raise a ValidationError

