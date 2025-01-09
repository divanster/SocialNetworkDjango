# backend/follows/schema.py

import graphene
from graphene_django.types import DjangoObjectType
from .models import Follow
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from .services import process_follow_event, notify_user_about_follow, publish_follow_event

# Get the custom User model
User = get_user_model()


# Define GraphQL Type for Follow model
class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Follows
class Query(graphene.ObjectType):
    all_follows = graphene.List(FollowType)
    follows_by_user = graphene.List(FollowType, user_id=graphene.Int(required=True))
    followers = graphene.List(FollowType, user_id=graphene.Int(required=True))
    following = graphene.List(FollowType, user_id=graphene.Int(required=True))

    # Resolve all follow relationships
    def resolve_all_follows(self, info, **kwargs):
        return Follow.objects.all()

    # Resolve follow relationships by user (both followers and following)
    def resolve_follows_by_user(self, info, user_id):
        return Follow.objects.filter(follower_id=user_id) | Follow.objects.filter(
            followed_id=user_id)

    # Resolve followers of a specific user
    def resolve_followers(self, info, user_id):
        return Follow.objects.filter(followed_id=user_id)

    # Resolve users followed by a specific user
    def resolve_following(self, info, user_id):
        return Follow.objects.filter(follower_id=user_id)


# Define Mutations for Creating and Deleting Follows
class CreateFollow(graphene.Mutation):
    class Arguments:
        followed_id = graphene.Int(required=True)  # ID of the user to be followed

    follow = graphene.Field(FollowType)

    def mutate(self, info, followed_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to follow a user.")

        try:
            followed = User.objects.get(id=followed_id)
        except User.DoesNotExist:
            raise GraphQLError("User to follow does not exist.")

        if Follow.objects.filter(follower=user, followed=followed, is_deleted=False).exists():
            raise GraphQLError("You are already following this user.")

        # Create the follow relationship
        follow = Follow.objects.create(follower=user, followed=followed)

        # Process the follow event (notify user and publish to Kafka)
        process_follow_event({'follow_id': follow.id})

        return CreateFollow(follow=follow)


class DeleteFollow(graphene.Mutation):
    class Arguments:
        followed_id = graphene.Int(required=True)  # ID of the user to unfollow

    success = graphene.Boolean()

    def mutate(self, info, followed_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to unfollow a user.")

        try:
            follow = Follow.objects.get(follower=user, followed_id=followed_id, is_deleted=False)
            follow.delete()  # Soft delete

            # Process the follow event (publish to Kafka)
            process_follow_event({'follow_id': follow.id})

            return DeleteFollow(success=True)
        except Follow.DoesNotExist:
            raise GraphQLError("Follow relationship does not exist.")


# Optional: RestoreFollow Mutation
class RestoreFollow(graphene.Mutation):
    class Arguments:
        follow_id = graphene.Int(required=True)  # ID of the follow to restore

    follow = graphene.Field(FollowType)

    def mutate(self, info, follow_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to restore a follow relationship.")

        try:
            follow_instance = Follow.all_objects.get(id=follow_id, is_deleted=True)
            if follow_instance.follower != user:
                raise GraphQLError("You do not have permission to restore this follow relationship.")

            follow_instance.restore()

            # Process the follow event (publish to Kafka)
            process_follow_event({'follow_id': follow_instance.id})

            return RestoreFollow(follow=follow_instance)
        except Follow.DoesNotExist:
            raise GraphQLError("Follow relationship does not exist or is not deleted.")


# Define Mutation Class to Group All Mutations for Follow
class Mutation(graphene.ObjectType):
    create_follow = CreateFollow.Field()
    delete_follow = DeleteFollow.Field()
    restore_follow = RestoreFollow.Field()  # Add this line if implementing restore


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
