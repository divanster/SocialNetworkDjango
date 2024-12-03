import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model

# Your other schema imports
import albums.schema
import users.schema
import stories.schema
import comments.schema
import friends.schema
import follows.schema
import notifications.schema
import reactions.schema
import tagging.schema
import newsfeed.schema
import social.schema
import messenger.schema

# Get the custom User model
User = get_user_model()


# Define the User GraphQL type
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name')  # Add other fields if needed


# Define the Query for 'me'
class MeQuery(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to view this information.")
        return user


# Combine Queries from all the different apps
class Query(
    albums.schema.Query,
    users.schema.Query,
    stories.schema.Query,
    comments.schema.Query,
    friends.schema.Query,
    follows.schema.Query,
    notifications.schema.Query,
    reactions.schema.Query,
    tagging.schema.Query,
    newsfeed.schema.Query,
    social.schema.Query,
    messenger.schema.Query,
    MeQuery,  # Add the MeQuery here to include the 'me' field
    graphene.ObjectType,
):
    pass


# Combine Mutations from all the different apps
class Mutation(
    albums.schema.Mutation,
    users.schema.Mutation,
    stories.schema.Mutation,
    comments.schema.Mutation,
    friends.schema.Mutation,
    follows.schema.Mutation,
    notifications.schema.Mutation,
    reactions.schema.Mutation,
    tagging.schema.Mutation,
    # newsfeed.schema.Mutation,
    social.schema.Mutation,
    messenger.schema.Mutation,
    graphene.ObjectType,
):
    pass


# Define the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
