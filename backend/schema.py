# backend/schema.py

import os
import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model

# Import your app schemas
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

from core.middleware import GraphQLLoggingMiddleware, GraphQLValidationMiddleware

# Get the custom User model
User = get_user_model()

# Define the User GraphQL type
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'last_name')  # Excluded 'first_name'

# Define the Query for 'me'
class MeQuery(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(self, info):
        user = info.context.get('user')
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
    newsfeed.schema.Mutation,
    social.schema.Mutation,
    messenger.schema.Mutation,
    graphene.ObjectType,
):
    pass

# Determine if middleware should be enabled
ENABLE_MIDDLEWARE = os.getenv('ENABLE_GRAPHQL_MIDDLEWARE', 'true').lower() in ['true', '1', 'yes']

# Define the middleware list based on the environment variable
middleware = []
if ENABLE_MIDDLEWARE:
    middleware = [
        GraphQLValidationMiddleware(schema=None),  # Placeholder, will set after schema creation
        GraphQLLoggingMiddleware(),
        # Add other middleware here if needed
    ]

# Define the schema with conditional middleware
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    middleware=middleware if middleware else None,
)

# After schema is defined, set it in validation middleware
if ENABLE_MIDDLEWARE:
    for mw in middleware:
        if isinstance(mw, GraphQLValidationMiddleware):
            mw.schema = schema
