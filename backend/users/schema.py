import graphene
from graphene_django.types import DjangoObjectType

from tagging.models import TaggedItem
from .models import CustomUser, UserProfile
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required, staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
import logging
import base64
import uuid
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

User = get_user_model()


# Define UserProfileType
class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        exclude = ('is_deleted', 'deleted_at')  # Exclude soft-deletion fields


# Define GraphQL Types for CustomUser
class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('is_deleted', 'deleted_at')  # Exclude soft-deletion fields

    # Custom fields for profile data
    first_name = graphene.String()
    last_name = graphene.String()
    profile_picture = graphene.String()

    # Resolvers to fetch these fields from the related UserProfile model
    def resolve_first_name(self, info):
        # Access the related UserProfile object
        profile = getattr(self, 'profile', None)
        if profile:
            return profile.first_name
        return None

    def resolve_last_name(self, info):
        # Access the related UserProfile object
        profile = getattr(self, 'profile', None)
        if profile:
            return profile.last_name
        return None

    def resolve_profile_picture(self, info):
        # Access the related UserProfile object
        profile = getattr(self, 'profile', None)
        if profile and profile.profile_picture:
            return info.context.build_absolute_uri(profile.profile_picture.url)
        elif profile and profile.profile_picture_url:
            return profile.profile_picture_url
        return None


# Helper function to get authenticated user
def get_authenticated_user(info):
    user = info.context.user
    if user.is_anonymous:
        raise GraphQLError("Authentication required.")
    return user


# Define Queries for Users
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType, page=graphene.Int(required=False),
                              page_size=graphene.Int(required=False))
    user_by_id = graphene.Field(UserType, id=graphene.UUID(required=True))
    user_profile_by_id = graphene.Field(UserProfileType,
                                        user_id=graphene.UUID(required=True))
    current_user = graphene.Field(UserType)

    # Resolve all users (restricted to admin users)
    @staff_member_required
    def resolve_all_users(self, info, page=1, page_size=10, **kwargs):
        offset = (page - 1) * page_size
        return CustomUser.objects.select_related("profile").filter(is_deleted=False)[
               offset:offset + page_size]

    # Resolve a specific user by ID
    def resolve_user_by_id(self, info, id):
        user = get_object_or_404(CustomUser.all_objects, id=id, is_deleted=False)
        return user

    # Resolve a specific user's profile by user ID
    def resolve_user_profile_by_id(self, info, user_id):
        profile = get_object_or_404(UserProfile.all_objects, user_id=user_id,
                                    is_deleted=False)
        return profile

    # Resolve the currently logged-in user's information
    @login_required
    def resolve_current_user(self, info):
        user = get_authenticated_user(info)
        return user


# Define Mutations for Creating, Updating, and Deleting Users and UserProfiles
class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)  # Added password2

    user = graphene.Field(UserType)

    def mutate(self, info, email, username, password, password2):
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise GraphQLError("Invalid email format.")

        # Validate password length
        if len(password) < 8:
            raise GraphQLError("Password must be at least 8 characters long.")

        # Check if passwords match
        if password != password2:
            raise GraphQLError("Passwords do not match.")

        # Check for unique email and username
        if CustomUser.all_objects.filter(email=email).exists():
            raise GraphQLError("A user with this email already exists.")

        if CustomUser.all_objects.filter(username=username).exists():
            raise GraphQLError("A user with this username already exists.")

        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            password=password
        )

        # Ensure a UserProfile is created for the new user
        UserProfile.objects.create(user=user)

        # Send welcome email via Celery task
        from kafka_app.tasks import send_welcome_email
        send_welcome_email.delay(user.id)

        return CreateUser(user=user)


class UpdateUserProfile(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        profile_picture = graphene.String()  # Base64 or URL; adjust as needed
        relationship_status = graphene.String()
        date_of_birth = graphene.String()
        gender = graphene.String()
        phone = graphene.String()
        town = graphene.String()
        country = graphene.String()
        bio = graphene.String()
        tagged_user_ids = graphene.List(graphene.UUID)  # Added for tag management

    user_profile = graphene.Field(UserProfileType)
    updated_fields = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        user = get_authenticated_user(info)
        try:
            user_profile = UserProfile.objects.get(user=user, is_deleted=False)
        except UserProfile.DoesNotExist:
            raise GraphQLError("UserProfile does not exist or is deleted.")

        updated_fields = []
        profile_picture = kwargs.get('profile_picture')
        if profile_picture:
            if profile_picture.startswith('data:image'):
                # Handle Base64-encoded image
                try:
                    format, imgstr = profile_picture.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                    user_profile.profile_picture = data
                    updated_fields.append('profile_picture')
                except Exception as e:
                    raise GraphQLError("Invalid image data.")
            else:
                # Assume it's a URL; validate and assign
                # Ensure your model has a 'profile_picture_url' field
                user_profile.profile_picture_url = profile_picture
                updated_fields.append('profile_picture_url')

        # Update other fields
        for key in ['first_name', 'last_name', 'relationship_status',
                    'date_of_birth', 'gender', 'phone', 'town',
                    'country', 'bio']:
            value = kwargs.get(key)
            if value is not None:
                setattr(user_profile, key, value)
                updated_fields.append(key)

        # Handle tagged_user_ids
        tagged_user_ids = kwargs.get('tagged_user_ids')
        if tagged_user_ids is not None:
            user_profile.tags.all().delete()
            for user_id in tagged_user_ids:
                TaggedItem.objects.create(
                    content_object=user_profile,
                    tagged_user_id=user_id,
                    tagged_by=user
                )
            updated_fields.append('tagged_user_ids')

        # Validate the user_profile
        try:
            user_profile.clean()
        except ValidationError as e:
            raise GraphQLError(e.message_dict)

        user_profile.save()

        # Trigger notification task
        from kafka_app.tasks import send_profile_update_notification
        send_profile_update_notification.delay(user.id)

        logger.info(f"Profile updated for user {user.id}, notification task scheduled.")

        return UpdateUserProfile(user_profile=user_profile,
                                 updated_fields=updated_fields)


class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        user = get_authenticated_user(info)
        if not user.is_staff and user.id != user_id:
            raise GraphQLError(
                "Permission denied. Only admin or the user themselves can delete their account.")

        try:
            user_to_delete = CustomUser.all_objects.get(id=user_id, is_deleted=False)
            user_to_delete.delete()  # Soft delete
            logger.info(f"Soft-deleted CustomUser with ID: {user_to_delete.id}")
            return DeleteUser(success=True)
        except CustomUser.DoesNotExist:
            raise GraphQLError("User not found or already deleted.")


class RestoreUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.UUID(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, user_id):
        try:
            user = CustomUser.all_objects.get(id=user_id, is_deleted=True)
            user.restore()  # Restore soft-deleted user
            logger.info(f"Restored CustomUser with ID: {user.id}")
            return RestoreUser(user=user)
        except CustomUser.DoesNotExist:
            raise GraphQLError("User not found or not deleted.")


class DeleteUserProfile(graphene.Mutation):
    class Arguments:
        user_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        user = get_authenticated_user(info)
        if not user.is_staff and user.id != user_id:
            raise GraphQLError(
                "Permission denied. Only admin or the user themselves can delete the profile.")

        try:
            user_profile = UserProfile.all_objects.get(user_id=user_id,
                                                       is_deleted=False)
            user_profile.delete()  # Soft delete
            logger.info(f"Soft-deleted UserProfile with ID: {user_profile.id}")
            return DeleteUserProfile(success=True)
        except UserProfile.DoesNotExist:
            raise GraphQLError("UserProfile not found or already deleted.")


class RestoreUserProfile(graphene.Mutation):
    class Arguments:
        user_id = graphene.UUID(required=True)

    user_profile = graphene.Field(UserProfileType)

    def mutate(self, info, user_id):
        try:
            user_profile = UserProfile.all_objects.get(user_id=user_id, is_deleted=True)
            user_profile.restore()
            logger.info(f"Restored UserProfile with ID: {user_profile.id}")
            return RestoreUserProfile(user_profile=user_profile)
        except UserProfile.DoesNotExist:
            raise GraphQLError("UserProfile not found or not deleted.")


# Mutation Class to Group All Mutations for User and UserProfile
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user_profile = UpdateUserProfile.Field()
    delete_user = DeleteUser.Field()
    restore_user = RestoreUser.Field()
    delete_user_profile = DeleteUserProfile.Field()
    restore_user_profile = RestoreUserProfile.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
