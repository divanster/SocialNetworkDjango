import graphene
from graphene_django.types import DjangoObjectType
from .models import FriendRequest, Friendship, Block
from django.contrib.auth import get_user_model
from graphql import GraphQLError

# Get the custom User model
User = get_user_model()

# Define GraphQL Types for FriendRequest, Friendship, and Block models
class FriendRequestType(DjangoObjectType):
    class Meta:
        model = FriendRequest
        fields = "__all__"  # Expose all fields of the model


class FriendshipType(DjangoObjectType):
    class Meta:
        model = Friendship
        fields = "__all__"  # Expose all fields of the model


class BlockType(DjangoObjectType):
    class Meta:
        model = Block
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Friends
class Query(graphene.ObjectType):
    all_friend_requests = graphene.List(FriendRequestType)
    all_friendships = graphene.List(FriendshipType)
    all_blocks = graphene.List(BlockType)
    friend_requests_by_user = graphene.List(FriendRequestType, user_id=graphene.Int(required=True))
    friendships_by_user = graphene.List(FriendshipType, user_id=graphene.Int(required=True))
    blocks_by_user = graphene.List(BlockType, user_id=graphene.Int(required=True))

    # Resolve all friend requests
    def resolve_all_friend_requests(self, info, **kwargs):
        return FriendRequest.objects.all()

    # Resolve all friendships
    def resolve_all_friendships(self, info, **kwargs):
        return Friendship.objects.all()

    # Resolve all blocks
    def resolve_all_blocks(self, info, **kwargs):
        return Block.objects.all()

    # Resolve friend requests by a specific user (sent and received)
    def resolve_friend_requests_by_user(self, info, user_id):
        return FriendRequest.objects.filter(sender_id=user_id) | FriendRequest.objects.filter(receiver_id=user_id)

    # Resolve friendships by user
    def resolve_friendships_by_user(self, info, user_id):
        return Friendship.objects.filter(user1_id=user_id) | Friendship.objects.filter(user2_id=user_id)

    # Resolve blocks by user
    def resolve_blocks_by_user(self, info, user_id):
        return Block.objects.filter(blocker_id=user_id) | Block.objects.filter(blocked_id=user_id)


# Define Mutations for Friend Requests, Friendships, and Blocks
class CreateFriendRequest(graphene.Mutation):
    class Arguments:
        receiver_id = graphene.Int(required=True)  # ID of the user to send a friend request to

    friend_request = graphene.Field(FriendRequestType)

    def mutate(self, info, receiver_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to send a friend request.")

        if user.id == receiver_id:
            raise GraphQLError("Cannot send a friend request to yourself.")

        if FriendRequest.objects.filter(sender=user, receiver_id=receiver_id, status='pending').exists():
            raise GraphQLError("A pending friend request already exists.")

        friend_request = FriendRequest.objects.create(sender=user, receiver_id=receiver_id)
        return CreateFriendRequest(friend_request=friend_request)


class RespondToFriendRequest(graphene.Mutation):
    class Arguments:
        friend_request_id = graphene.Int(required=True)
        accept = graphene.Boolean(required=True)

    success = graphene.Boolean()

    def mutate(self, info, friend_request_id, accept):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to respond to a friend request.")

        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=user, status='pending')
        except FriendRequest.DoesNotExist:
            raise GraphQLError("Friend request not found or already responded to.")

        if accept:
            friend_request.accept()
        else:
            friend_request.reject()

        return RespondToFriendRequest(success=True)


class BlockUser(graphene.Mutation):
    class Arguments:
        blocked_id = graphene.Int(required=True)  # ID of the user to block

    block = graphene.Field(BlockType)

    def mutate(self, info, blocked_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to block a user.")

        if user.id == blocked_id:
            raise GraphQLError("Cannot block yourself.")

        if Block.objects.filter(blocker=user, blocked_id=blocked_id).exists():
            raise GraphQLError("You have already blocked this user.")

        block = Block.objects.create(blocker=user, blocked_id=blocked_id)
        return BlockUser(block=block)


class Mutation(graphene.ObjectType):
    create_friend_request = CreateFriendRequest.Field()
    respond_to_friend_request = RespondToFriendRequest.Field()
    block_user = BlockUser.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
