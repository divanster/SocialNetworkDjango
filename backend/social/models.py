from mongoengine import Document, StringField, IntField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField, EmbeddedDocumentListField, DateTimeField
from core.models.base_models import MongoBaseModel, MongoUUIDModel, MongoSoftDeleteModel
from datetime import datetime
from django.core.exceptions import ValidationError
import uuid
import os


# Helper function for generating file paths for post images
def post_image_file_path(instance, filename):
    """
    Helper function to generate a file path for new post images.
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/post/', filename)


class Rating(EmbeddedDocument):
    """
    Embedded Document for storing Ratings related to a Post.
    """
    user_id = IntField(required=True, help_text="ID of the user giving the rating")
    user_username = StringField(max_length=150, required=True,
                                help_text="Username of the user giving the rating")
    value = IntField(min_value=1, max_value=5, required=True,
                     help_text="Rating value between 1 and 5")

    def clean(self):
        """
        Custom validation to ensure the rating value is within the acceptable range.
        """
        if self.value < 1 or self.value > 5:
            raise ValidationError('Rating value must be between 1 and 5.')

    def __str__(self):
        return f"Rating {self.value} Stars by User {self.user_username}"


class PostImage(EmbeddedDocument):
    """
    Embedded Document to store image information related to a post.
    """
    post_image_id = StringField(default=lambda: str(uuid.uuid4()), required=True,
                                help_text="Unique ID for the image")
    image = StringField(required=True, help_text="Path to the image file")

    def __str__(self):
        return f"Image for Post"


class Post(MongoUUIDModel, MongoSoftDeleteModel, MongoBaseModel):
    """
    Main Document for storing Posts.
    Utilizes MongoDB through MongoEngine for storing nested data and improving performance.
    """
    post_id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()),
                          required=True,
                          help_text="Unique ID for the post")
    title = StringField(max_length=255, required=True, help_text="Title of the post")
    content = StringField(help_text="Content of the post")
    author_id = IntField(required=True, help_text="ID of the author")
    author_username = StringField(max_length=150, required=True,
                                  help_text="Username of the author")
    tags = ListField(StringField(max_length=50), default=list,
                     help_text="List of tags related to the post")
    images = EmbeddedDocumentListField(PostImage, default=list,
                                       help_text="List of images related to the post")
    ratings = EmbeddedDocumentListField(Rating, default=list,
                                        help_text="List of ratings related to the post")

    meta = {
        'collection': 'posts',
        'indexes': [
            'author_id',  # Index to allow efficient query of posts by author
            'tags',  # Index to allow efficient search by tags
        ],
    }

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save method to update 'updated_at' timestamp on every update.
        """
        if self.pk:
            self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """
        Calculate the average rating of the post.
        """
        if self.ratings:
            return sum(rating.value for rating in self.ratings) / len(self.ratings)
        return 0
