import graphene
from graphene_django.types import DjangoObjectType
from .models import CustomUser, UserProfile
from graphql import GraphQLError
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()

# Define GraphQL Types for CustomUser and UserProfile models
class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "is_active", "is_staff", "date_joined"]  # Expose selected fields


class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Users
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))
    user_profile_by_id = graphene.Field(UserProfileType, user_id=graphene.Int(required=True))
    current_user = graphene.Field(UserType)

    # Resolve all users (restricted to admin users)
    def resolve_all_users(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Permission denied. Only admin users can access all users.")
        return User.objects.all()

    # Resolve a specific user by ID
    def resolve_user_by_id(self, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise GraphQLError("User not found.")

    # Resolve a specific user's profile by user ID
    def resolve_user_profile_by_id(self, info, user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            raise GraphQLError("User profile not found.")

    # Resolve the currently logged-in user's information
    def resolve_current_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to view current user information.")
        return user


# Define Mutations for Creating and Updating Users and UserProfiles
class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, username, password):
        if User.objects.filter(email=email).exists():
            raise GraphQLError("A user with this email already exists.")
        if User.objects.filter(username=username).exists():
            raise GraphQLError("A user with this username already exists.")
        user = User.objects.create_user(email=email, username=username, password=password)
        return CreateUser(user=user)


class UpdateUserProfile(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        date_of_birth = graphene.String()
        gender = graphene.String()
        phone = graphene.String()
        town = graphene.String()
        country = graphene.String()
        bio = graphene.String()

    user_profile = graphene.Field(UserProfileType)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to update the profile.")

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        for key, value in kwargs.items():
            if value is not None:
                setattr(user_profile, key, value)
        user_profile.clean()  # Perform custom validation
        user_profile.save()
        return UpdateUserProfile(user_profile=user_profile)


# Mutation Class to Group All Mutations for User and UserProfile
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user_profile = UpdateUserProfile.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
