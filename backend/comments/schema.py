import graphene
from graphene_django.types import DjangoObjectType
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from graphene import UUID
from graphql import GraphQLError


# Define GraphQL Type for Comment model
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"  # Expose all fields of the model

    # Custom field to return the object type that this comment is related to
    content_object = graphene.String()

    def resolve_content_object(self, info):
        return str(self.content_object)


# Define Queries for Comments
class Query(graphene.ObjectType):
    all_comments = graphene.List(CommentType)
    comment_by_id = graphene.Field(CommentType, id=graphene.UUID(required=True))
    comments_for_object = graphene.List(CommentType,
                                        content_type_id=graphene.Int(required=True),
                                        object_id=UUID(required=True))

    # Resolve all comments
    def resolve_all_comments(self, info, **kwargs):
        return Comment.objects.all()

    # Resolve a specific comment by its ID
    def resolve_comment_by_id(self, info, id):
        try:
            return Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return None

    # Resolve comments for a specific content type and object
    def resolve_comments_for_object(self, info, content_type_id, object_id):
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            return Comment.objects.filter(content_type=content_type,
                                          object_id=object_id)
        except ContentType.DoesNotExist:
            raise GraphQLError("Content type does not exist.")


# Define Mutations for Creating Comments
class CreateComment(graphene.Mutation):
    class Arguments:
        content_type_id = graphene.Int(required=True)  # ID of the ContentType
        object_id = UUID(required=True)  # ID of the object to comment on
        content = graphene.String(required=True)  # Content of the comment

    comment = graphene.Field(CommentType)

    def mutate(self, info, content_type_id, object_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to add a comment.")

        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            raise GraphQLError("Invalid content type.")

        # Create the comment
        comment = Comment.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            content=content
        )
        return CreateComment(comment=comment)


# Mutation Class to Group All Mutations for Comments
class Mutation(graphene.ObjectType):
    create_comment = CreateComment.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
