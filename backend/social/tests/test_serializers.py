import pytest
from social.serializers import PostSerializer, RatingSerializer
from social.models import Post, Rating
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_post_serializer():
    user = User.objects.create_user(email='test@example.com', password='password123')
    post = Post.objects.create(title='Test Post', content='This is a test post.',
                               author=user)
    serializer = PostSerializer(post)
    data = serializer.data

    assert data['title'] == post.title
    assert data['content'] == post.content
    assert data['author'] == user.email


@pytest.mark.django_db
def test_rating_serializer():
    user = User.objects.create_user(email='test@example.com', password='password123')
    post = Post.objects.create(title='Test Post', content='This is a test post.')
    rating = Rating.objects.create(value=5, user=user, post=post)
    serializer = RatingSerializer(rating)
    data = serializer.data

    assert data['value'] == rating.value
    assert data['user'] == user.id
