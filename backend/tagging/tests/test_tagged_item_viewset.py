# tagging/tests/test_tagged_item_viewset.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tagging.models import TaggedItem

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_tagged_item_create(api_client):
    user = User.objects.create_user(email='user@example.com', password='testpass', username='testuser')
    api_client.force_authenticate(user)
    data = {
        'tagged_item_type': 'Post',
        'tagged_item_id': '1',
        'tagged_user_id': user.id,
        'tagged_by': user.id,
    }
    response = api_client.post('/api/v1/tagging/', data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_tagged_item_list(api_client):
    user = User.objects.create_user(email='user@example.com', password='testpass', username='testuser')
    api_client.force_authenticate(user)
    response = api_client.get('/api/v1/tagging/')
    assert response.status_code == status.HTTP_200_OK
