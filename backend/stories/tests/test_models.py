from django.test import TestCase
from stories.models import Story


class TestStoryModel(TestCase):

    def test_create_story(self):
        story = Story.objects.create(
            user_id=1,
            user_username="test_user",
            content="This is a test story"
        )
        self.assertEqual(str(story), f"Story by test_user at {story.created_at}")
        self.assertEqual(Story.objects.count(), 1)

    def test_story_ordering(self):
        story1 = Story.objects.create(user_id=1, user_username="user1",
                                      content="First story")
        story2 = Story.objects.create(user_id=2, user_username="user2",
                                      content="Second story")

        # The most recently created story should come first
        stories = Story.objects.all()
        self.assertEqual(stories.first(), story2)
        self.assertEqual(stories.last(), story1)
