# backend/newsfeed/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story
from .serializers import AggregatedFeedSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    user = request.user
    # Aggregate content from various models
    posts = Post.objects.select_related('author').prefetch_related('comments', 'reactions', 'tags').order_by(
        '-created_at')
    comments = Comment.objects.select_related('user', 'post').order_by('-created_at')
    reactions = Reaction.objects.select_related('user', 'post').order_by('-created_at')
    albums = Album.objects.select_related('user').prefetch_related('photos').order_by('-created_at')
    stories = Story.objects.select_related('user').order_by('-created_at')

    # Serialize the aggregated content
    feed_data = {
        'posts': posts,
        'comments': comments,
        'reactions': reactions,
        'albums': albums,
        'stories': stories
    }
    serializer = AggregatedFeedSerializer(feed_data)

    return Response(serializer.data)
