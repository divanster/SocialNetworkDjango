# newsfeed/views.py

from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination

from social.serializers import PostSerializer
from comments.serializers import CommentSerializer
from reactions.serializers import ReactionSerializer
from albums.serializers import AlbumSerializer
from tagging.serializers import TaggedItemSerializer
from friends.serializers import FriendRequestSerializer, FriendshipSerializer
from stories.serializers import StorySerializer
from .serializers import AggregatedFeedSerializer  # Only if defined in newsfeed/serializers.py

from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from tagging.models import TaggedItem
from friends.models import FriendRequest, Friendship
from stories.models import Story
import logging
from django.db import models

logger = logging.getLogger(__name__)


class AggregatedFeedPagination(PageNumberPagination):
    """Custom pagination for the aggregated feed."""
    page_size = 10  # Default items per page
    page_size_query_param = 'page_size'
    max_page_size = 50


class AggregatedFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            logger.debug(f"Fetching aggregated feed for user: {user.id}")

            # Fetch posts visible to the user
            posts = Post.objects.visible_to_user(user) \
                .select_related('user') \
                .prefetch_related('comments', 'tags', 'images', 'ratings') \
                .order_by('-created_at')
            logger.debug(f"Fetched posts count: {posts.count()}")

            # Serialize posts
            post_serializer = PostSerializer(posts, many=True)

            # Extract post IDs from the queryset (do not use serialized data here)
            post_ids = posts.values_list('id', flat=True)

            # Fetch comments related to the posts
            post_content_type = ContentType.objects.get_for_model(Post)
            comments = Comment.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched comments count: {comments.count()}")

            # Serialize comments
            comment_serializer = CommentSerializer(comments, many=True)

            # Fetch reactions related to the posts
            reactions = Reaction.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('user').order_by('-created_at')
            logger.debug(f"Fetched reactions count: {reactions.count()}")

            # Serialize reactions
            reaction_serializer = ReactionSerializer(reactions, many=True)

            # Fetch albums related to user
            albums = Album.objects.visible_to_user(user).select_related(
                'user').order_by('-created_at')
            logger.debug(f"Fetched albums count: {albums.count()}")

            # Serialize albums
            album_serializer = AlbumSerializer(albums, many=True)

            # Fetch tagged items
            tagged_items = TaggedItem.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('tagged_user', 'tagged_by').order_by('-created_at')
            logger.debug(f"Fetched tagged items count: {tagged_items.count()}")

            # Serialize tagged items
            tagged_item_serializer = TaggedItemSerializer(tagged_items, many=True)

            # Fetch friend requests and friendships
            friend_requests = FriendRequest.objects.filter(
                receiver=user
            ).select_related('sender', 'receiver').order_by('-created_at')
            logger.debug(f"Fetched friend requests count: {friend_requests.count()}")

            friendships = Friendship.objects.filter(
                models.Q(user1=user) | models.Q(user2=user)
            ).select_related('user1', 'user2').order_by('-created_at')
            logger.debug(f"Fetched friendships count: {friendships.count()}")

            # Serialize friend requests and friendships
            friend_request_serializer = FriendRequestSerializer(friend_requests, many=True)
            friendship_serializer = FriendshipSerializer(friendships, many=True)

            # Fetch stories visible to the user
            stories = Story.objects.visible_to_user(user).select_related(
                'user').order_by('-created_at')
            logger.debug(f"Fetched stories count: {stories.count()}")

            # Serialize stories
            story_serializer = StorySerializer(stories, many=True)

            # Organize data for aggregation and serialization
            feed_data = {
                'posts': post_serializer.data,
                'comments': comment_serializer.data,
                'reactions': reaction_serializer.data,
                'albums': album_serializer.data,
                'tagged_items': tagged_item_serializer.data,
                'stories': story_serializer.data,
                'friend_requests': friend_request_serializer.data,
                'friendships': friendship_serializer.data,
            }

            logger.debug(f"Feed data to be serialized: {feed_data}")

            # Directly return the aggregated serialized data without additional serialization
            return Response(feed_data)

        except AuthenticationFailed as auth_err:
            logger.error(f"Authentication error: {auth_err}")
            return Response({"detail": "Authentication failed."}, status=401)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"detail": f"An unexpected error occurred: {str(e)}"}, status=500)
