import graphene
from graphene_django.types import DjangoObjectType
from .models import CustomUser, UserProfile
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required, staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

User = get_user_model()


# Define GraphQL Types for CustomUser and UserProfile models
class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "is_active", "is_staff", "date_joined"]


class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = "__all__"


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
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))
    user_profile_by_id = graphene.Field(UserProfileType,
                                        user_id=graphene.Int(required=True))
    current_user = graphene.Field(UserType)

    # Resolve all users (restricted to admin users)
    @staff_member_required
    def resolve_all_users(self, info, page=1, page_size=10, **kwargs):
        offset = (page - 1) * page_size
        return User.objects.select_related("profile").all()[offset:offset + page_size]

    # Resolve a specific user by ID
    def resolve_user_by_id(self, info, id):
        return get_object_or_404(User, id=id)

    # Resolve a specific user's profile by user ID
    def resolve_user_profile_by_id(self, info, user_id):
        return get_object_or_404(UserProfile, user_id=user_id)

    # Resolve the currently logged-in user's information
    @login_required
    def resolve_current_user(self, info):
        return info.context.user


# Define Mutations for Creating, Updating, and Deleting Users and UserProfiles
class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, username, password):
        try:
            validate_email(email)
        except ValidationError:
            raise GraphQLError("Invalid email format.")

        if len(password) < 8:
            raise GraphQLError("Password must be at least 8 characters long.")

        if User.objects.filter(email=email).exists():
            raise GraphQLError("A user with this email already exists.")

        if User.objects.filter(username=username).exists():
            raise GraphQLError("A user with this username already exists.")

        user = User.objects.create_user(email=email, username=username,
                                        password=password)
        return CreateUser(user=user)


class UpdateUserProfile(graphene.Mutation):
    class Arguments:
        date_of_birth = graphene.String()
        gender = graphene.String()
        phone = graphene.String()
        town = graphene.String()
        country = graphene.String()
        bio = graphene.String()

    user_profile = graphene.Field(UserProfileType)
    updated_fields = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        user = get_authenticated_user(info)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        updated_fields = []

        for key, value in kwargs.items():
            if value is not None:
                setattr(user_profile, key, value)
                updated_fields.append(key)

        user_profile.clean()
        user_profile.save()
        return UpdateUserProfile(user_profile=user_profile,
                                 updated_fields=updated_fields)


class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        user = get_authenticated_user(info)
        if not user.is_staff and user.id != user_id:
            raise GraphQLError(
                "Permission denied. Only admin or the user themselves can delete their account.")

        user_to_delete = get_object_or_404(User, id=user_id)
        user_to_delete.delete()
        return DeleteUser(success=True)


class DeleteUserProfile(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        user = get_authenticated_user(info)
        if not user.is_staff and user.id != user_id:
            raise GraphQLError(
                "Permission denied. Only admin or the user themselves can delete the "
                "profile.")

        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        user_profile.delete()
        return DeleteUserProfile(success=True)


# Mutation Class to Group All Mutations for User and UserProfile
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user_profile = UpdateUserProfile.Field()
    delete_user = DeleteUser.Field()
    delete_user_profile = DeleteUserProfile.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
