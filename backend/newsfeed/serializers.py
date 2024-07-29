# backend/newsfeed/serializers.py
from rest_framework import serializers
from social.serializers import PostSerializer
from comments.serializers import CommentSerializer
from reactions.serializers import ReactionSerializer
from albums.serializers import AlbumSerializer
from stories.serializers import StorySerializer


class AggregatedFeedSerializer(serializers.Serializer):
    posts = PostSerializer(many=True)
    comments = CommentSerializer(many=True)
    reactions = ReactionSerializer(many=True)
    albums = AlbumSerializer(many=True)
    stories = StorySerializer(many=True)
