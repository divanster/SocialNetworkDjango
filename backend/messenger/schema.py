import graphene
from graphene_django.types import DjangoObjectType

from friends.models import Block
from .models import Message
from django.contrib.auth import get_user_model
from graphql import GraphQLError

# Get the custom User model
User = get_user_model()

# Define GraphQL Type for Message model
class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Messages
class Query(graphene.ObjectType):
    all_messages = graphene.List(MessageType)
    messages_between_users = graphene.List(MessageType, user1_id=graphene.Int(required=True), user2_id=graphene.Int(required=True))
    received_messages = graphene.List(MessageType, is_read=graphene.Boolean())

    # Resolve all messages (restricted to admin users)
    def resolve_all_messages(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Permission denied. Only admin users can access all messages.")
        return Message.objects.all()

    # Resolve messages between two specific users
    def resolve_messages_between_users(self, info, user1_id, user2_id):
        user = info.context.user
        if user.id not in [user1_id, user2_id] and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view messages involving yourself.")
        return Message.objects.filter(
            sender_id__in=[user1_id, user2_id],
            receiver_id__in=[user1_id, user2_id]
        ).order_by('-created_at')

    # Resolve received messages of the logged-in user
    def resolve_received_messages(self, info, is_read=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to view received messages.")
        messages = Message.objects.filter(receiver=user)
        if is_read is not None:
            messages = messages.filter(is_read=is_read)
        return messages.order_by('-created_at')


# Define Mutations for Sending and Marking Messages
class SendMessage(graphene.Mutation):
    class Arguments:
        receiver_id = graphene.UUID(required=True)  # Changed to UUID for consistency
        content = graphene.String(required=True)  # Content of the message

    message = graphene.Field(MessageType)

    def mutate(self, info, receiver_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to send a message.")

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise GraphQLError("Receiver not found.")

        # Check if the sender has blocked the receiver
        if Block.objects.filter(blocker=user, blocked=receiver).exists():
            raise GraphQLError("You have blocked this user and cannot send messages to them.")

        message = Message.objects.create(sender=user, receiver=receiver, content=content)
        return SendMessage(message=message)


class MarkMessageAsRead(graphene.Mutation):
    class Arguments:
        message_id = graphene.UUID(required=True)  # ID of the message to mark as read

    success = graphene.Boolean()

    def mutate(self, info, message_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to mark a message as read.")

        try:
            message = Message.objects.get(id=message_id, receiver=user)
            if not message.is_read:
                message.mark_as_read()
            return MarkMessageAsRead(success=True)
        except Message.DoesNotExist:
            raise GraphQLError("Message not found or permission denied.")


# Mutation Class to Group All Mutations for Messenger
class Mutation(graphene.ObjectType):
    send_message = SendMessage.Field()
    mark_message_as_read = MarkMessageAsRead.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
