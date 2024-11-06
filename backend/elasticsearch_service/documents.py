from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from social.models import Post
from comments.models import Comment
from pages.models import Page
from albums.models import Album
from stories.models import Story

# =======================
# Post Document
# =======================
@registry.register_document
class PostDocument(Document):
    author = fields.ObjectField(properties={
        'username': fields.TextField(),
    })
    title = fields.TextField()
    content = fields.TextField()
    visibility = fields.TextField()
    created_at = fields.DateField()

    class Index:
        name = 'posts'

    class Django:
        model = Post
        fields = ['id']

# =======================
# Comment Document
# =======================
@registry.register_document
class CommentDocument(Document):
    user = fields.ObjectField(properties={
        'username': fields.TextField(),
    })
    content = fields.TextField()
    post_id = fields.IntegerField()

    class Index:
        name = 'comments'

    class Django:
        model = Comment
        fields = ['id', 'created_at']

# =======================
# Page Document
# =======================
@registry.register_document
class PageDocument(Document):
    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.TextField(),
    })  # Representing the user relationship with an ObjectField
    title = fields.TextField()
    content = fields.TextField()
    created_at = fields.DateField()

    class Index:
        name = 'pages'

    class Django:
        model = Page
        fields = ['id']  # Removed 'user_id', represented via ObjectField instead

# =======================
# Album Document
# =======================
@registry.register_document
class AlbumDocument(Document):
    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.TextField(),
    })  # Representing the user relationship with an ObjectField
    title = fields.TextField()
    description = fields.TextField()
    created_at = fields.DateField()

    class Index:
        name = 'albums'

    class Django:
        model = Album
        fields = ['id']  # Removed 'user_id', represented via ObjectField instead

# =======================
# Story Document
# =======================
@registry.register_document
class StoryDocument(Document):
    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.TextField(),
    })  # Representing the user relationship with an ObjectField
    content = fields.TextField()
    media_type = fields.TextField()
    created_at = fields.DateField()
    is_active = fields.BooleanField()

    class Index:
        name = 'stories'

    class Django:
        model = Story
        fields = ['id']  # Removed 'user_id', represented via ObjectField instead
