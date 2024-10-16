# tagging/tests/test_signals.py
import pytest
from tagging.models import TaggedItem
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_tagged_item_created_signal():
    tagged_by = User.objects.create(username="tagger", email="tagger@example.com")
    tagged_user = User.objects.create(username="tagged", email="tagged@example.com")

    tagged_item = TaggedItem.objects.create(
        tagged_item_type='Post',
        tagged_item_id='1234',
        tagged_user_id=tagged_user.id,
        tagged_user_username=tagged_user.username,
        tagged_by_id=tagged_by.id,
        tagged_by_username=tagged_by.username,
    )

    # Check if notification was created
    assert Notification.objects.filter(
        receiver_id=tagged_user.id, sender_id=tagged_by.id).exists()


@pytest.mark.django_db
def test_tagged_item_deleted_signal():
    tagged_by = User.objects.create(username="tagger", email="tagger@example.com")
    tagged_user = User.objects.create(username="tagged", email="tagged@example.com")

    tagged_item = TaggedItem.objects.create(
        tagged_item_type='Post',
        tagged_item_id='1234',
        tagged_user_id=tagged_user.id,
        tagged_user_username=tagged_user.username,
        tagged_by_id=tagged_by.id,
        tagged_by_username=tagged_by.username,
    )

    tagged_item.delete()
    # No assertions - primarily making sure no exceptions occur and print statements are triggered.
