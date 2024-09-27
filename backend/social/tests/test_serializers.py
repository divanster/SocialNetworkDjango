# backend/social/tests/test_serializers.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from social.models import Post, PostImage, Rating, Tag
from social.serializers import PostSerializer, PostImageSerializer, RatingSerializer, \
    TagSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

User = get_user_model()


class PostSerializerTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='serializeruser@example.com',
            username='serializeruser',
            password='serializerpassword'
        )
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_post_serializer_create(self):
        image = SimpleUploadedFile('test_image.jpg', b'file_content',
                                   content_type='image/jpeg')
        data = {
            'title': 'Serialized Post',
            'content': 'Content for serialized post.',
            'image_files': [image],
            'tagged_user_ids': [],
        }
        serializer = PostSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save(author=self.user)
        self.assertEqual(post.title, 'Serialized Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.images.count(), 1)
        self.assertEqual(post.images.first().image.name.endswith('test_image.jpg'),
                         True)

    def test_post_serializer_validation(self):
        data = {
            'title': '',
            'content': 'No title post.',
        }
        serializer = PostSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)


class RatingSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='ratingserializer@example.com',
            username='ratingserializer',
            password='ratingpassword'
        )
        self.post = Post.objects.create(
            title='Rating Serializer Post',
            content='Content for rating serializer post.',
            author=self.user
        )

    def test_rating_serializer_create(self):
        data = {
            'value': 5,
            'user': self.user.id,
        }
        serializer = RatingSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        rating = serializer.save(post=self.post)
        self.assertEqual(rating.value, 5)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.post, self.post)

    def test_rating_serializer_invalid_value(self):
        data = {
            'value': 6,  # Invalid rating
            'user': self.user.id,
        }
        serializer = RatingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)


class TagSerializerTests(TestCase):

    def test_tag_serializer(self):
        tag = Tag.objects.create(name='Serializer Tag')
        serializer = TagSerializer(instance=tag)
        data = serializer.data
        self.assertEqual(data['name'], 'Serializer Tag')
