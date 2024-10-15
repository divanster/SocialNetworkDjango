from django.test import TestCase
from reactions.models import Reaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class ReactionModelTest(TestCase):

    def setUp(self):
        # Creating a test user
        self.user = User.objects.create_user(
            username='testuser', password='password123'
        )

        self.reaction_data = {
            "user_id": self.user.id,
            "user_username": self.user.username,
            "reacted_item_type": "Post",
            "reacted_item_id": "1",
            "emoji": "like",
        }

    def test_create_reaction(self):
        # Test creating a Reaction instance
        reaction = Reaction.objects.create(**self.reaction_data)
        self.assertEqual(Reaction.objects.count(), 1)
        self.assertEqual(reaction.emoji, "like")
        self.assertEqual(reaction.user_username, "testuser")
        self.assertEqual(reaction.reacted_item_type, "Post")

    def test_unique_constraint(self):
        # Create a reaction and try to create a duplicate
        Reaction.objects.create(**self.reaction_data)
        with self.assertRaises(ValidationError):
            duplicate_reaction = Reaction(**self.reaction_data)
            duplicate_reaction.full_clean()  # This triggers the unique constraint validation

    def test_multiple_reactions_on_same_item(self):
        # Test that the same user can react multiple times with different emojis on the same item
        Reaction.objects.create(**self.reaction_data)
        different_emoji_data = self.reaction_data.copy()
        different_emoji_data["emoji"] = "love"
        reaction2 = Reaction.objects.create(**different_emoji_data)
        self.assertEqual(Reaction.objects.count(), 2)
        self.assertNotEqual(reaction2.emoji, "like")
        self.assertEqual(reaction2.emoji, "love")

    def test_reaction_string_representation(self):
        # Test the __str__ method of the Reaction model
        reaction = Reaction.objects.create(**self.reaction_data)
        self.assertEqual(str(reaction),
                         f"{self.user.username} reacted with like on Post 1")

    def test_reaction_creation_invalid_emoji(self):
        # Test that creating a Reaction with an invalid emoji raises a ValidationError
        invalid_reaction_data = self.reaction_data.copy()
        invalid_reaction_data["emoji"] = "invalid_emoji"
        with self.assertRaises(ValidationError):
            invalid_reaction = Reaction(**invalid_reaction_data)
            invalid_reaction.full_clean()  # This triggers the field validation

    def test_reaction_unique_together(self):
        # Ensure unique constraint for user_id, reacted_item_type, reacted_item_id,
        # emoji
        Reaction.objects.create(**self.reaction_data)
        # Creating another reaction with the same data should raise an error
        with self.assertRaises(ValidationError):
            reaction_duplicate = Reaction(**self.reaction_data)
            reaction_duplicate.full_clean()

    def test_reaction_different_users_same_emoji(self):
        # Test that different users can react with the same emoji to the same item
        another_user = User.objects.create_user(
            username='anotheruser', password='password123'
        )

        Reaction.objects.create(**self.reaction_data)

        different_user_reaction_data = self.reaction_data.copy()
        different_user_reaction_data["user_id"] = another_user.id
        different_user_reaction_data["user_username"] = another_user.username

        reaction2 = Reaction.objects.create(**different_user_reaction_data)
        self.assertEqual(Reaction.objects.count(), 2)
        self.assertEqual(reaction2.user_username, "anotheruser")

    def test_delete_reaction(self):
        # Test the deletion of a reaction
        reaction = Reaction.objects.create(**self.reaction_data)
        self.assertEqual(Reaction.objects.count(), 1)
        reaction.delete()
        self.assertEqual(Reaction.objects.count(), 0)

    def test_reaction_related_fields(self):
        # Test that the correct fields are set after a reaction is created
        reaction = Reaction.objects.create(**self.reaction_data)
        self.assertEqual(reaction.user_id, self.user.id)
        self.assertEqual(reaction.user_username, self.user.username)
        self.assertEqual(reaction.reacted_item_type, "Post")
        self.assertEqual(reaction.reacted_item_id, "1")
        self.assertEqual(reaction.emoji, "like")
