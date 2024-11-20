import graphene
from graphene_django.types import DjangoObjectType
from .models import Notification
from django.contrib.contenttypes.models import ContentType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphene import UUID

# Get the custom User model
User = get_user_model()

# Define GraphQL Type for Notification model
class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"  # Expose all fields of the model

    # Custom field to represent the related content type
    content_object = graphene.String()

    def resolve_content_object(self, info):
        return str(self.content_object) if self.content_object else None


# Define Queries for Notifications
class Query(graphene.ObjectType):
    all_notifications = graphene.List(NotificationType)
    notifications_by_user = graphene.List(NotificationType, user_id=graphene.Int(required=True))
    unread_notifications = graphene.List(NotificationType, user_id=graphene.Int(required=True))

    # Resolve all notifications (restricted to admin users)
    def resolve_all_notifications(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Permission denied. Only admin users can access all notifications.")
        return Notification.objects.all()

    # Resolve notifications for a specific user
    def resolve_notifications_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own notifications.")
        return Notification.objects.filter(receiver_id=user_id).order_by('-created_at')

    # Resolve unread notifications for a specific user
    def resolve_unread_notifications(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own notifications.")
        return Notification.objects.filter(receiver_id=user_id, is_read=False).order_by('-created_at')


# Define Mutations for Marking Notifications as Read
class MarkNotificationAsRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.UUID(required=True)  # ID of the notification to mark as read

    success = graphene.Boolean()

    def mutate(self, info, notification_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to mark a notification as read.")

        try:
            notification = Notification.objects.get(id=notification_id, receiver=user)
            if not notification.is_read:
                notification.mark_as_read()
            return MarkNotificationAsRead(success=True)
        except Notification.DoesNotExist:
            raise GraphQLError("Notification not found or permission denied.")


# Mutation Class to Group All Mutations for Notifications
class Mutation(graphene.ObjectType):
    mark_notification_as_read = MarkNotificationAsRead.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
