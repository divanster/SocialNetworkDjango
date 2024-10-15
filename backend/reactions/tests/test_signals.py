from django.test import TestCase
from reactions.models import Reaction
from unittest.mock import patch


class TestReactionSignals(TestCase):
    def setUp(self):
        self.reaction_data = {
            "user_id": 1,
            "user_username": "test_user",
            "reacted_item_type": "Post",
            "reacted_item_id": "1",
            "emoji": "like",
        }

    @patch('reactions.signals.send_reaction_event_to_kafka.delay')
    def test_reaction_created_signal(self, mock_send_reaction_event):
        reaction = Reaction.objects.create(**self.reaction_data)
        mock_send_reaction_event.assert_called_once_with(reaction.id, 'created')

    @patch('reactions.signals.send_reaction_event_to_kafka.delay')
    def test_reaction_deleted_signal(self, mock_send_reaction_event):
        reaction = Reaction.objects.create(**self.reaction_data)
        reaction.delete()
        mock_send_reaction_event.assert_called_once_with(reaction.id, 'deleted')
