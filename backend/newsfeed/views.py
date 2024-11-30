from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from .serializers import AggregatedFeedSerializer
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from tagging.models import TaggedItem
from friends.models import FriendRequest, Friendship
import logging

logger = logging.getLogger(__name__)

class AggregatedFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles the request to get the aggregated feed data for the authenticated user.
        """
        try:
            user = request.user  # Get the authenticated user
            logger.debug(f"Fetching aggregated feed for user: {user.id}")

            # Fetch posts with visibility settings
            posts = Post.objects.visible_to_user(user) \
                .select_related('author') \
                .prefetch_related('comments', 'reactions', 'tags', 'images', 'ratings') \
                .order_by('-created_at')
            logger.debug(f"Fetched posts: {posts.values('id', 'title')}")

            # Fetch comments related to the posts (use content_type to filter)
            post_content_type = ContentType.objects.get_for_model(Post)
            comments = Comment.objects.filter(
                content_type=post_content_type,
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched comments: {comments.count()}")

            # Fetch reactions related to the posts (use content_type to filter)
            reactions = Reaction.objects.filter(
                content_type=post_content_type,
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched reactions: {reactions.count()}")

            # Fetch albums related to the posts (assuming ForeignKey directly to Post)
            albums = Album.objects.filter(post__in=posts).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched albums: {albums.count()}")

            # Similarly, fetch tagged items
            tagged_items = TaggedItem.objects.filter(
                content_type=ContentType.objects.get_for_model(Post),
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched tagged items: {tagged_items.count()}")

            # Fetch friend requests and friendships
            friend_requests = FriendRequest.objects.filter(to_user=user).select_related(
                'from_user', 'to_user').order_by('-created_at')
            friendships = Friendship.objects.filter(user=user).select_related(
                'friend').order_by('-created_at')

            # Organize data for serialization
            feed_data = {
                'posts': posts,
                'comments': comments,
                'reactions': reactions,
                'albums': albums,
                'tagged_items': tagged_items,
                'friend_requests': friend_requests,
                'friendships': friendships,
            }

            # Serialize and return data
            serializer = AggregatedFeedSerializer(feed_data)
            return Response(serializer.data)

        except AuthenticationFailed as auth_err:
            logger.error(f"Authentication error: {auth_err}")
            return Response({"detail": "Authentication failed."}, status=401)

        except Exception as e:
            logger.error(f"Error fetching feed data: {e}")
            return Response({"detail": "An error occurred while fetching data."}, status=500)
