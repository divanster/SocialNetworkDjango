import pytest
from albums.models import Album, Photo
from django.contrib.auth import get_user_model
from uuid import UUID

User = get_user_model()


# Define reusable pytest fixture for user creation
@pytest.fixture
@pytest.mark.django_db
def create_user():
    return User.objects.create(email='test@example.com', username='testuser')


@pytest.fixture
@pytest.mark.django_db
def create_album(create_user):
    return Album.objects.using('social_db').create(user=create_user, title="Test Album",
                                                   description="This is a test album")


# Test to create an album and verify its attributes
@pytest.mark.django_db(databases=['social_db'])
def test_create_album(create_user):
    album = Album.objects.using('social_db').create(user=create_user,
                                                    title="Test Album",
                                                    description="This is a test album")

    assert album.title == "Test Album"
    assert album.description == "This is a test album"
    assert album.user == create_user
    assert isinstance(album.id, UUID)  # Verify album ID is a UUID
    assert not album.is_deleted


# Test to create a photo and verify its attributes
@pytest.mark.django_db(databases=['social_db'])
def test_create_photo(create_album):
    photo = Photo.objects.using('social_db').create(album=create_album,
                                                    description="Test Photo")

    assert photo.album == create_album
    assert photo.description == "Test Photo"
    assert isinstance(photo.id, UUID)  # Verify photo ID is a UUID
    assert not photo.is_deleted
