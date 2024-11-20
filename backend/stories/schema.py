import graphene
from graphene_django.types import DjangoObjectType
from .models import Story
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphene import UUID

# Get the custom User model
User = get_user_model()

# Define GraphQL Type for Story model
class StoryType(DjangoObjectType):
    class Meta:
        model = Story
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Stories
class Query(graphene.ObjectType):
    all_stories = graphene.List(StoryType)
    story_by_id = graphene.Field(StoryType, story_id=graphene.UUID(required=True))
    stories_by_user = graphene.List(StoryType, user_id=graphene.Int(required=True))

    # Resolve all stories visible to the logged-in user
    def resolve_all_stories(self, info, **kwargs):
        user = info.context.user
        return Story.objects.visible_to_user(user)

    # Resolve a specific story by its ID
    def resolve_story_by_id(self, info, story_id):
        try:
            user = info.context.user
            return Story.objects.visible_to_user(user).get(id=story_id)
        except Story.DoesNotExist:
            raise GraphQLError("Story not found or you do not have permission to view it.")

    # Resolve stories created by a specific user
    def resolve_stories_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own stories.")
        return Story.objects.filter(user_id=user_id)


# Define Mutations for Creating, Viewing, and Deactivating Stories
class CreateStory(graphene.Mutation):
    class Arguments:
        content = graphene.String()
        media_type = graphene.String(default_value="text")
        media_url = graphene.String()
        visibility = graphene.String(default_value="friends")

    story = graphene.Field(StoryType)

    def mutate(self, info, content=None, media_type="text", media_url=None, visibility="friends"):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to create a story.")

        story = Story.objects.create(
            user=user,
            content=content,
            media_type=media_type,
            media_url=media_url,
            visibility=visibility
        )
        return CreateStory(story=story)


class MarkStoryAsViewed(graphene.Mutation):
    class Arguments:
        story_id = graphene.UUID(required=True)  # ID of the story to mark as viewed

    success = graphene.Boolean()

    def mutate(self, info, story_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to mark a story as viewed.")

        try:
            story = Story.objects.get(id=story_id)
            story.add_view(user)
            return MarkStoryAsViewed(success=True)
        except Story.DoesNotExist:
            raise GraphQLError("Story not found or permission denied.")


class DeactivateStory(graphene.Mutation):
    class Arguments:
        story_id = graphene.UUID(required=True)  # ID of the story to deactivate

    success = graphene.Boolean()

    def mutate(self, info, story_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to deactivate a story.")

        try:
            story = Story.objects.get(id=story_id, user=user)
            story.deactivate_story()
            return DeactivateStory(success=True)
        except Story.DoesNotExist:
            raise GraphQLError("Story not found or permission denied.")


# Mutation Class to Group All Mutations for Stories
class Mutation(graphene.ObjectType):
    create_story = CreateStory.Field()
    mark_story_as_viewed = MarkStoryAsViewed.Field()
    deactivate_story = DeactivateStory.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
