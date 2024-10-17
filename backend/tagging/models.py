from django.db import models


class TaggedItem(models.Model):
    """
    Stores a tag of a user on any model instance.
    Uses PostgreSQL to enforce unique constraints and maintain relationships.
    """

    # Fields to define the type and ID of the tagged item
    tagged_item_type = models.CharField(
        max_length=100,
        help_text="Type of the item being tagged (e.g., Post, Comment)"
    )
    tagged_item_id = models.CharField(
        max_length=255,
        help_text="ID of the item being tagged"
    )

    # Fields to define information about the tagged user
    tagged_user_id = models.IntegerField(help_text="ID of the user being tagged")
    tagged_user_username = models.CharField(
        max_length=150,
        help_text="Username of the user being tagged"
    )

    # Fields to define information about the tagging action
    tagged_by_id = models.IntegerField(help_text="ID of the user who tagged")
    tagged_by_username = models.CharField(
        max_length=150,
        help_text="Username of the user who performed the tagging"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the tag was created"
    )

    class Meta:
        unique_together = ('tagged_item_type', 'tagged_item_id', 'tagged_user_id')
        ordering = ['-timestamp']
        verbose_name = 'Tagged Item'
        verbose_name_plural = 'Tagged Items'

    def __str__(self):
        return (
            f"{self.tagged_by_username} tagged {self.tagged_user_username} on "
            f"{self.tagged_item_type} {self.tagged_item_id}"
        )
