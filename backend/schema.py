import graphene
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
