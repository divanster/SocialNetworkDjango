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
from django.contrib.contenttypes.models import ContentType


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

            # Fetch posts, comments, reactions, albums, etc.
            posts = Post.objects.visible_to_user(user) \
                .select_related('author') \
                .prefetch_related('comments', 'reactions', 'tags', 'images', 'ratings') \
                .order_by('-created_at')
            logger.debug(f"Fetched {posts.count()} posts")

            # Get the ContentType for the Post model
            post_content_type = ContentType.objects.get_for_model(Post)

            # Fetch comments related to the posts
            comments = Comment.objects.filter(
                content_type=post_content_type,  # Use content_type from ContentType
                object_id__in=posts.values('id')  # Use object_id from Post IDs
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched {comments.count()} comments")

            # Fetch reactions (assuming they are related to posts similarly)
            reactions = Reaction.objects.filter(
                content_type=post_content_type,
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched {reactions.count()} reactions")

            # Fetch albums related to the posts (similar to the comments query)
            albums = Album.objects.filter(
                content_type=post_content_type,
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched {albums.count()} albums")

            # Similarly, fetch stories, tagged items, friend requests, friendships, etc.

            tagged_items = TaggedItem.objects.filter(
                content_type=post_content_type,
                object_id__in=posts.values('id')
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched {tagged_items.count()} tagged items")

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
