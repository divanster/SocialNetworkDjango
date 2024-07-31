from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story
from .serializers import AggregatedFeedSerializer


class UserFeedView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AggregatedFeedSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        posts = Post.objects.filter(author=user)\
            .select_related('author')\
            .prefetch_related('comments', 'reactions', 'tags', 'images', 'ratings')\
            .order_by('-created_at')

        comments = Comment.objects.filter(user=user)\
            .select_related('user', 'post')\
            .order_by('-created_at')

        reactions = Reaction.objects.filter(user=user)\
            .select_related('user', 'post')\
            .order_by('-created_at')

        albums = Album.objects.filter(user=user)\
            .select_related('user')\
            .prefetch_related('photos')\
            .order_by('-created_at')

        stories = Story.objects.filter(user=user)\
            .select_related('user')\
            .order_by('-created_at')

        feed_data = {
            'posts': posts,
            'comments': comments,
            'reactions': reactions,
            'albums': albums,
            'stories': stories
        }

        serializer = self.get_serializer(feed_data)
        return Response(serializer.data)
