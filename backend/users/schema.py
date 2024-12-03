import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import UserProfile

# CustomUser GraphQL Type
class CustomUserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'is_active', 'is_staff', 'date_joined']

    first_name = graphene.String()
    last_name = graphene.String()
    profile_picture = graphene.String()

    # Resolve fields from the UserProfile model
    def resolve_first_name(self, info):
        return self.profile.first_name if hasattr(self, 'profile') else None

    def resolve_last_name(self, info):
        return self.profile.last_name if hasattr(self, 'profile') else None

    def resolve_profile_picture(self, info):
        return self.profile.profile_picture.url if self.profile and self.profile.profile_picture else None


# UserProfile GraphQL Type
class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'gender', 'date_of_birth',
                  'profile_picture', 'bio', 'phone', 'town', 'country', 'relationship_status']


# Query class to provide the ability to fetch data from GraphQL
class Query(graphene.ObjectType):
    user = graphene.Field(CustomUserType, id=graphene.ID(required=True))
    profile = graphene.Field(UserProfileType, id=graphene.ID(required=True))
    all_users = graphene.List(CustomUserType)
    all_profiles = graphene.List(UserProfileType)

    # Resolver to get a user by ID
    def resolve_user(self, info, id):
        try:
            return get_user_model().objects.get(pk=id)
        except get_user_model().DoesNotExist:
            return None

    # Resolver to get a profile by ID
    def resolve_profile(self, info, id):
        try:
            return UserProfile.objects.get(pk=id)
        except UserProfile.DoesNotExist:
            return None

    # Resolver to get all users
    def resolve_all_users(self, info):
        return get_user_model().objects.all()

    # Resolver to get all profiles
    def resolve_all_profiles(self, info):
        return UserProfile.objects.all()


# Mutation to create or update UserProfile
class UserProfileInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    gender = graphene.String()
    date_of_birth = graphene.Date()
    bio = graphene.String()
    phone = graphene.String()
    town = graphene.String()
    country = graphene.String()
    relationship_status = graphene.String()


# Update User Profile Mutation
class UpdateUserProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UserProfileInput(required=True)

    user_profile = graphene.Field(UserProfileType)

    @classmethod
    def mutate(cls, root, info, id, input):
        try:
            profile = UserProfile.objects.get(user_id=id)
            for key, value in input.items():
                setattr(profile, key, value)
            profile.save()
            return UpdateUserProfile(user_profile=profile)
        except UserProfile.DoesNotExist:
            return UpdateUserProfile(user_profile=None)


# Delete User Profile Mutation
class DeleteUserProfile(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            profile = UserProfile.objects.get(pk=id)
            profile.delete()
            return DeleteUserProfile(success=True)
        except UserProfile.DoesNotExist:
            return DeleteUserProfile(success=False)


# Define the Mutation class to include update and delete operations
class Mutation(graphene.ObjectType):
    update_user_profile = UpdateUserProfile.Field()
    delete_user_profile = DeleteUserProfile.Field()


# Define the GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
