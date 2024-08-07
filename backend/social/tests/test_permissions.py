import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from social.permissions import IsAuthorOrReadOnly
from social.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_is_author_or_read_only_permission():
    factory = APIRequestFactory()
    user = User.objects.create_user(email='author@example.com', password='password123')
    another_user = User.objects.create_user(email='another@example.com',
                                            password='password123')
    post = Post.objects.create(title='Test Post', content='This is a test post.',
                               author=user)

    request = factory.get('/')
    request.user = user
    permission = IsAuthorOrReadOnly()

    # Check if author has permission
    assert permission.has_object_permission(request, None, post) == True

    # Check if another user does not have permission
    request.user = another_user
    assert permission.has_object_permission(request, None, post) == False
