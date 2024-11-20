import graphene
from graphene_django.types import DjangoObjectType
from .models import Reaction
from django.contrib.contenttypes.models import ContentType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphene import UUID

# Get the custom User model
User = get_user_model()


# Define GraphQL Type for Reaction model
class ReactionType(DjangoObjectType):
    class Meta:
        model = Reaction
        fields = "__all__"  # Expose all fields of the model

    # Custom field to represent the related content type
    content_object = graphene.String()

    def resolve_content_object(self, info):
        return str(self.content_object) if self.content_object else None


# Define Queries for Reactions
class Query(graphene.ObjectType):
    all_reactions = graphene.List(ReactionType)
    reactions_by_user = graphene.List(ReactionType, user_id=graphene.Int(required=True))
    reactions_for_content = graphene.List(ReactionType,
                                          content_type_id=graphene.Int(required=True),
                                          object_id=UUID(required=True))

    # Resolve all reactions (restricted to admin users)
    def resolve_all_reactions(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError(
                "Permission denied. Only admin users can access all reactions.")
        return Reaction.objects.all()

    # Resolve reactions made by a specific user
    def resolve_reactions_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError(
                "Permission denied. You can only view your own reactions.")
        return Reaction.objects.filter(user_id=user_id).order_by('-created_at')

    # Resolve reactions for a specific content type and object
    def resolve_reactions_for_content(self, info, content_type_id, object_id):
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            return Reaction.objects.filter(content_type=content_type,
                                           object_id=object_id).order_by('-created_at')
        except ContentType.DoesNotExist:
            raise GraphQLError("Content type does not exist.")


# Define Mutations for Creating and Deleting Reactions
class CreateReaction(graphene.Mutation):
    class Arguments:
        content_type_id = graphene.Int(required=True)  # ID of the ContentType
        object_id = UUID(required=True)  # ID of the object to react to
        emoji = graphene.String(required=True)  # Emoji to react with

    reaction = graphene.Field(ReactionType)

    def mutate(self, info, content_type_id, object_id, emoji):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to react.")

        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            raise GraphQLError("Invalid content type.")

        # Ensure unique constraint for user, content_type, object_id, and emoji
        if Reaction.objects.filter(user=user, content_type=content_type,
                                   object_id=object_id, emoji=emoji).exists():
            raise GraphQLError(
                "You have already reacted to this content with this emoji.")

        # Create the reaction
        reaction = Reaction.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            emoji=emoji
        )
        return CreateReaction(reaction=reaction)


class DeleteReaction(graphene.Mutation):
    class Arguments:
        reaction_id = graphene.UUID(required=True)  # ID of the reaction to delete

    success = graphene.Boolean()

    def mutate(self, info, reaction_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to delete a reaction.")

        try:
            reaction = Reaction.objects.get(id=reaction_id, user=user)
            reaction.delete()
            return DeleteReaction(success=True)
        except Reaction.DoesNotExist:
            raise GraphQLError("Reaction not found or permission denied.")


# Mutation Class to Group All Mutations for Reactions
class Mutation(graphene.ObjectType):
    create_reaction = CreateReaction.Field()
    delete_reaction = DeleteReaction.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
