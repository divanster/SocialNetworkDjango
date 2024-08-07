import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from social.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_post_list_view():
    client = APIClient()
    response = client.get(reverse('post-list'))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_post_view():
    client = APIClient()
    user = User.objects.create_user(email='test@example.com', password='password123')
    client.force_authenticate(user=user)
    data = {
        'title': 'Test Post',
        'content': 'This is a test post.'
    }
    response = client.post(reverse('post-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Post.objects.count() == 1
