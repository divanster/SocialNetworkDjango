import pytest
from django.contrib.auth import get_user_model
from social.models import Post, PostImage, Tag, Rating

User = get_user_model()


@pytest.mark.django_db
def test_create_post():
    user = User.objects.create_user(email='test@example.com', password='password123')
    post = Post.objects.create(title='Test Post', content='This is a test post.',
                               author=user)
    assert post.title == 'Test Post'
    assert post.author == user


@pytest.mark.django_db
def test_create_post_image():
    post = Post.objects.create(title='Test Post', content='This is a test post.')
    post_image = PostImage.objects.create(post=post, image='test_image.png')
    assert post_image.post == post


@pytest.mark.django_db
def test_create_tag():
    tag = Tag.objects.create(name='Django')
    assert tag.name == 'Django'


@pytest.mark.django_db
def test_create_rating():
    user = User.objects.create_user(email='test@example.com', password='password123')
    post = Post.objects.create(title='Test Post', content='This is a test post.')
    rating = Rating.objects.create(value=5, user=user, post=post)
    assert rating.value == 5
    assert rating.user == user
    assert rating.post == post
