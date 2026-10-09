import importlib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from stories.models import Story
from stories.tasks import deactivate_expired_stories


class CeleryConsistencyTests(TestCase):
    def test_celery_beat_schedule_targets_resolve(self):
        schedule = settings.CELERY_BEAT_SCHEDULE
        self.assertTrue(schedule)

        for entry in schedule.values():
            task_path = entry.get('task')
            self.assertIsNotNone(task_path)
            module_path, attr_name = task_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            task = getattr(module, attr_name, None)
            self.assertTrue(callable(task), msg=f"Task target is not callable: {task_path}")

    def test_wave_tasks_imports_resolve(self):
        task_paths = [
            "kafka_app.tasks.user_tasks.process_user_event_task",
            "kafka_app.tasks.user_tasks.send_welcome_email",
            "kafka_app.tasks.follow_tasks.process_follow_event_task",
            "kafka_app.tasks.friend_tasks.process_friend_event_task",
            "kafka_app.tasks.social_tasks.process_post_event_task",
            "kafka_app.tasks.comment_tasks.process_comment_event_task",
            "kafka_app.tasks.reaction_tasks.process_reaction_event_task",
            "kafka_app.tasks.messenger_tasks.process_message_event_task",
            "kafka_app.tasks.notification_tasks.process_notification_event_task",
            "stories.tasks.deactivate_expired_stories",
        ]

        for task_path in task_paths:
            module_path, attr_name = task_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            task = getattr(module, attr_name, None)
            self.assertTrue(callable(task), msg=f"Task import failed: {task_path}")

    def test_deactivate_expired_stories_runs_synchronously(self):
        user = get_user_model().objects.create_user(
            email='wave5-celery-user@example.com',
            username='wave5_celery_user',
            password='StrongPass123!',
        )

        old_story = Story.objects.create(
            user=user,
            content='old story',
            media_type='text',
            is_active=True,
        )
        Story.objects.filter(id=old_story.id).update(created_at=timezone.now() - timedelta(hours=25))

        fresh_story = Story.objects.create(
            user=user,
            content='fresh story',
            media_type='text',
            is_active=True,
        )

        updated = deactivate_expired_stories()
        self.assertEqual(updated, 1)

        old_story.refresh_from_db()
        fresh_story.refresh_from_db()
        self.assertFalse(old_story.is_active)
        self.assertTrue(fresh_story.is_active)
