from unittest import TestCase, mock
from reactions.tasks import send_reaction_event_to_kafka
from reactions.models import Reaction


class TestReactionTasks(TestCase):
    def setUp(self):
        self.reaction_data = {
            "user_id": 1,
            "user_username": "test_user",
            "reacted_item_type": "Post",
            "reacted_item_id": "1",
            "emoji": "like",
        }
        self.reaction = Reaction.objects.create(**self.reaction_data)

    @mock.patch('kafka_app.producer.KafkaProducerClient.send_message')
    def test_send_reaction_event_to_kafka(self, mock_send_message):
        send_reaction_event_to_kafka(self.reaction.id, 'created')

        mock_send_message.assert_called_once()
        call_args = mock_send_message.call_args[0]
        assert call_args[0] == 'REACTION_EVENTS'
        assert 'reaction_id' in call_args[1]
