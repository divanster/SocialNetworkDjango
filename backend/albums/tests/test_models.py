import pytest
from albums.models import Album, Photo
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db(databases=['social_db'])
def test_create_album():
    user = User.objects.create(email='test@example.com', username='testuser')
    album = Album.objects.using('social_db').create(user=user, title="Test Album",
                                                    description="This is a test album")

    assert album.title == "Test Album"
    assert album.description == "This is a test album"
    assert album.user == user


@pytest.mark.django_db(databases=['social_db'])
def test_create_photo():
    user = User.objects.create(email='test@example.com', username='testuser')
    album = Album.objects.using('social_db').create(user=user, title="Test Album")
    photo = Photo.objects.using('social_db').create(album=album,
                                                    description="Test Photo")

    assert photo.album == album
    assert photo.description == "Test Photo"
