# elasticsearch_service/management/commands/reindex_posts.py

from django.core.management.base import BaseCommand
from social.models import Post
from elasticsearch_service.documents import PostDocument


class Command(BaseCommand):
    help = 'Reindex all Post instances into Elasticsearch'

    def handle(self, *args, **kwargs):
        posts = Post.objects.all()
        for post in posts:
            PostDocument().update(post)
        self.stdout.write(self.style.SUCCESS('Successfully reindexed all posts.'))
