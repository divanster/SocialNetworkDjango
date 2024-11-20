import graphene
from graphene_django.types import DjangoObjectType
from albums.models import Album
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from stories.models import Story
from tagging.models import TaggedItem
from notifications.models import Notification
from follows.models import Follow
from friends.models import FriendRequest, Friendship
from messenger.models import Message
from django.contrib.auth import get_user_model
from django.db import models


# Get the custom User model
User = get_user_model()

# Define GraphQL Types for Newsfeed items
class AlbumType(DjangoObjectType):
    class Meta:
        model = Album
        fields = "__all__"


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class ReactionType(DjangoObjectType):
    class Meta:
        model = Reaction
        fields = "__all__"


class StoryType(DjangoObjectType):
    class Meta:
        model = Story
        fields = "__all__"


class TaggedItemType(DjangoObjectType):
    class Meta:
        model = TaggedItem
        fields = "__all__"


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = "__all__"


class FriendRequestType(DjangoObjectType):
    class Meta:
        model = FriendRequest
        fields = "__all__"


class FriendshipType(DjangoObjectType):
    class Meta:
        model = Friendship
        fields = "__all__"


class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"


# Define the NewsfeedItem GraphQL type to aggregate all types of items
class NewsfeedItemType(graphene.Union):
    class Meta:
        types = (
            PostType,
            AlbumType,
            CommentType,
            ReactionType,
            StoryType,
            TaggedItemType,
            NotificationType,
            FollowType,
            FriendRequestType,
            FriendshipType,
            MessageType
        )


# Define Queries for the Newsfeed
class Query(graphene.ObjectType):
    newsfeed = graphene.List(NewsfeedItemType)

    def resolve_newsfeed(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to view the newsfeed.")

        # Collect data from different models to populate the newsfeed
        posts = Post.objects.visible_to_user(user)
        albums = Album.objects.filter(user=user)
        comments = Comment.objects.filter(user=user)
        reactions = Reaction.objects.filter(user=user)
        stories = Story.objects.visible_to_user(user)
        tags = TaggedItem.objects.filter(tagged_user=user)
        notifications = Notification.objects.filter(receiver=user)
        follows = Follow.objects.filter(follower=user)
        friend_requests = FriendRequest.objects.filter(receiver=user)
        friendships = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
        messages = Message.objects.filter(receiver=user)

        # Aggregate all items and sort them by created_at
        newsfeed_items = (
            list(posts) +
            list(albums) +
            list(comments) +
            list(reactions) +
            list(stories) +
            list(tags) +
            list(notifications) +
            list(follows) +
            list(friend_requests) +
            list(friendships) +
            list(messages)
        )
        newsfeed_items.sort(key=lambda x: x.created_at, reverse=True)

        return newsfeed_items


# Create the schema combining Query for Newsfeed
schema = graphene.Schema(query=Query)
