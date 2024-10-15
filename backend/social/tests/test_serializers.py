from django.test import TestCase
from rest_framework import serializers
from django.contrib.auth import get_user_model
from social.models import Post, PostImage, Rating
from social.serializers import PostSerializer, PostImageSerializer, RatingSerializer
from tagging.models import TaggedItem
from tagging.serializers import TaggedItemSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import MagicMock

User = get_user_model()


class PostSerializerTest(TestCase):

    def setUp(self):
        # Create users for testing
        self.author = User.objects.create_user(
            username='author', email='author@example.com', password='password123')
        self.tagged_user = User.objects.create_user(
            username='taggeduser', email='tagged@example.com', password='password123')

        # Create a simple image file for testing image uploads
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'some image content',
            content_type='image/jpeg'
        )

        self.post_data = {
            'title': 'Test Post',
            'content': 'This is a test post content.',
            'image_files': [self.image_file],
            'tagged_user_ids': [self.tagged_user.id]
        }

    def test_post_serializer_create(self):
        # Simulate a request context
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # Check that the post was created correctly
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'This is a test post content.')
        self.assertEqual(post.author_id, self.author.id)
        self.assertEqual(post.author_username, self.author.username)

        # Check that the images were associated with the post
        self.assertEqual(post.images.count(), 1)
        post_image = post.images.first()
        self.assertIsNotNone(post_image.image)

        # Check that tagged users were created
        tagged_items = TaggedItem.objects.filter(content_object=post)
        self.assertEqual(tagged_items.count(), 1)
        self.assertEqual(tagged_items.first().tagged_user_id, self.tagged_user.id)

    def test_post_serializer_validation(self):
        # Test validation of image files
        invalid_data = self.post_data.copy()
        invalid_data['image_files'] = ['not an image']
        serializer = PostSerializer(data=invalid_data, context={'request': MagicMock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image_files', serializer.errors)

        # Test validation of tagged_user_ids
        invalid_data = self.post_data.copy()
        invalid_data['tagged_user_ids'] = ['invalid_id']
        serializer = PostSerializer(data=invalid_data, context={'request': MagicMock()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('tagged_user_ids', serializer.errors)

    def test_post_serializer_read_only_fields(self):
        # Attempt to write to read-only fields
        invalid_data = self.post_data.copy()
        invalid_data['author'] = 'malicious_user'
        serializer = PostSerializer(data=invalid_data, context={'request': MagicMock()})
        self.assertTrue(serializer.is_valid())
        post = serializer.save()
        self.assertNotEqual(post.author_username, 'malicious_user')

    def test_post_serializer_partial_update(self):
        # Test updating an existing post
        request = MagicMock()
        request.user = self.author

        # Create initial post
        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # Update the post
        update_data = {'title': 'Updated Title'}
        serializer = PostSerializer(post, data=update_data, partial=True,
                                    context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_post = serializer.save()

        self.assertEqual(updated_post.title, 'Updated Title')

    def test_post_serializer_invalid_user_tags(self):
        # Test with invalid user IDs in tagged_user_ids
        invalid_user_id = 9999  # Assuming this user ID doesn't exist
        invalid_data = self.post_data.copy()
        invalid_data['tagged_user_ids'] = [invalid_user_id]
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=invalid_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # TaggedItem should not be created for invalid user IDs
        tagged_items = TaggedItem.objects.filter(content_object=post)
        self.assertEqual(tagged_items.count(), 0)

    def test_post_serializer_no_images_or_tags(self):
        # Test creating a post without images or tagged users
        data = {
            'title': 'No Images or Tags',
            'content': 'Content without images or tags.'
        }
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        self.assertEqual(post.images.count(), 0)
        tagged_items = TaggedItem.objects.filter(content_object=post)
        self.assertEqual(tagged_items.count(), 0)

    def test_post_serializer_with_multiple_images(self):
        # Test creating a post with multiple images
        image_file_2 = SimpleUploadedFile(
            name='test_image_2.jpg',
            content=b'some other image content',
            content_type='image/jpeg'
        )
        data = self.post_data.copy()
        data['image_files'] = [self.image_file, image_file_2]
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        self.assertEqual(post.images.count(), 2)

    def test_post_serializer_response(self):
        # Test the serializer output data
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # Serialize the post to check output
        output_serializer = PostSerializer(post, context={'request': request})
        output_data = output_serializer.data

        self.assertEqual(output_data['title'], 'Test Post')
        self.assertEqual(output_data['author'], self.author.username)
        self.assertEqual(len(output_data['images']), 1)
        self.assertEqual(len(output_data['user_tags']), 1)
        self.assertEqual(output_data['user_tags'][0]['tagged_user']['username'],
                         self.tagged_user.username)
        self.assertNotIn('image_files', output_data)
        self.assertNotIn('tagged_user_ids', output_data)

    def test_post_serializer_invalid_data(self):
        # Test serializer with missing required fields
        invalid_data = {}
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=invalid_data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('content', serializer.errors)

    def test_post_serializer_create_tagged_items(self):
        # Test the create_tagged_items method
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # Ensure the tagged items are created correctly
        tagged_items = TaggedItem.objects.filter(content_object=post)
        self.assertEqual(tagged_items.count(), 1)
        tagged_item = tagged_items.first()
        self.assertEqual(tagged_item.tagged_user_id, self.tagged_user.id)
        self.assertEqual(tagged_item.tagged_by, self.author)

    def test_post_serializer_update(self):
        # Test updating an existing post with new images and tags
        request = MagicMock()
        request.user = self.author

        # Create initial post
        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()

        # Prepare new data for update
        new_tagged_user = User.objects.create_user(
            username='newtaggeduser', email='newtagged@example.com',
            password='password123')
        new_image_file = SimpleUploadedFile(
            name='new_test_image.jpg',
            content=b'new image content',
            content_type='image/jpeg'
        )
        update_data = {
            'content': 'Updated content.',
            'image_files': [new_image_file],
            'tagged_user_ids': [new_tagged_user.id]
        }

        serializer = PostSerializer(post, data=update_data, partial=True,
                                    context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_post = serializer.save()

        self.assertEqual(updated_post.content, 'Updated content.')
        self.assertEqual(updated_post.images.count(), 2)  # Original image + new image
        self.assertEqual(updated_post.user_tags.count(), 2)  # Original tag + new tag

    def test_post_serializer_invalid_image_files(self):
        # Test with invalid image files (non-image files)
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'some text content',
            content_type='text/plain'
        )
        data = self.post_data.copy()
        data['image_files'] = [invalid_file]
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image_files', serializer.errors)

    def test_post_serializer_empty_image_files(self):
        # Test with empty image_files list
        data = self.post_data.copy()
        data['image_files'] = []
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()
        self.assertEqual(post.images.count(), 0)

    def test_post_serializer_non_existent_tagged_user_ids(self):
        # Test with non-existent tagged user IDs
        data = self.post_data.copy()
        data['tagged_user_ids'] = [9999]  # Assuming 9999 does not exist
        request = MagicMock()
        request.user = self.author

        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()
        self.assertEqual(post.user_tags.count(), 0)
