from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    AggregatedFeedSerializer, PostSerializer, CommentSerializer, ReactionSerializer,
    AlbumSerializer, TaggedItemSerializer, FriendRequestSerializer,
    FriendshipSerializer, StorySerializer
)
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

            # Initialize pagination
            paginator = AggregatedFeedPagination()

            # Fetch and paginate posts
            posts = Post.objects.visible_to_user(user) \
                .select_related('user') \
                .prefetch_related('comments', 'tags', 'images', 'ratings') \
                .order_by('-created_at')
            paginated_posts = paginator.paginate_queryset(posts, request)
            post_serializer = PostSerializer(paginated_posts, many=True)
            post_ids = posts.values_list('id', flat=True)

            # Fetch and serialize comments
            post_content_type = ContentType.objects.get_for_model(Post)
            comments = Comment.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('user').order_by('-created_at')
            comment_serializer = CommentSerializer(comments, many=True)

            # Fetch and serialize reactions
            reactions = Reaction.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('user').order_by('-created_at')
            reaction_serializer = ReactionSerializer(reactions, many=True)

            # Fetch and serialize albums
            albums = Album.objects.visible_to_user(user).select_related(
                'user').order_by('-created_at')
            album_serializer = AlbumSerializer(albums, many=True)

            # Fetch and serialize tagged items
            tagged_items = TaggedItem.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).select_related('tagged_user', 'tagged_by').order_by('-created_at')
            tagged_item_serializer = TaggedItemSerializer(tagged_items, many=True)

            # Fetch and serialize friend requests
            friend_requests = FriendRequest.objects.filter(
                receiver=user
            ).select_related('sender', 'receiver').order_by('-created_at')
            friend_request_serializer = FriendRequestSerializer(friend_requests,
                                                                many=True)

            # Fetch and serialize friendships
            friendships = Friendship.objects.filter(
                models.Q(user1=user) | models.Q(user2=user)
            ).select_related('user1', 'user2').order_by('-created_at')
            friendship_serializer = FriendshipSerializer(friendships, many=True)

            # Fetch and serialize stories
            stories = Story.objects.visible_to_user(user).select_related(
                'user').order_by('-created_at')
            story_serializer = StorySerializer(stories, many=True)

            # Aggregate all serialized data
            feed_data = {
                'posts': post_serializer.data,
                'comments': comment_serializer.data,
                'reactions': reaction_serializer.data,
                'albums': album_serializer.data,
                'tagged_items': tagged_item_serializer.data,
                'friend_requests': friend_request_serializer.data,
                'friendships': friendship_serializer.data,
                'stories': story_serializer.data,
            }

            logger.debug(f"Feed data to be serialized: {feed_data}")

            # Use AggregatedFeedSerializer for validation and formatting
            serializer = AggregatedFeedSerializer(data=feed_data)
            serializer.is_valid(raise_exception=True)  # Validate the data

            # Return paginated response with validated data
            return paginator.get_paginated_response(serializer.data)

        except AuthenticationFailed as auth_err:
            logger.error(f"Authentication error: {auth_err}")
            return Response({"detail": "Authentication failed."}, status=401)

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response({"detail": "An unexpected error occurred."}, status=500)
