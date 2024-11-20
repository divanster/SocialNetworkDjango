import graphene
from graphene_django.types import DjangoObjectType
from .models import TaggedItem
from django.contrib.contenttypes.models import ContentType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphene import UUID

# Get the custom User model
User = get_user_model()

# Define GraphQL Type for TaggedItem model
class TaggedItemType(DjangoObjectType):
    class Meta:
        model = TaggedItem
        fields = "__all__"  # Expose all fields of the model

    # Custom field to represent the related content type
    content_object = graphene.String()

    def resolve_content_object(self, info):
        return str(self.content_object) if self.content_object else None


# Define Queries for Tagged Items
class Query(graphene.ObjectType):
    all_tags = graphene.List(TaggedItemType)
    tags_by_user = graphene.List(TaggedItemType, user_id=graphene.Int(required=True))
    tags_for_content = graphene.List(TaggedItemType, content_type_id=graphene.Int(required=True), object_id=UUID(required=True))

    # Resolve all tags (restricted to admin users)
    def resolve_all_tags(self, info, **kwargs):
        user = info.context.user
        if not user.is_staff:
            raise GraphQLError("Permission denied. Only admin users can access all tags.")
        return TaggedItem.objects.all()

    # Resolve tags involving a specific user
    def resolve_tags_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view tags involving yourself.")
        return TaggedItem.objects.filter(models.Q(tagged_user_id=user_id) | models.Q(tagged_by_id=user_id)).order_by('-created_at')

    # Resolve tags for a specific content type and object
    def resolve_tags_for_content(self, info, content_type_id, object_id):
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            return TaggedItem.objects.filter(content_type=content_type, object_id=object_id).order_by('-created_at')
        except ContentType.DoesNotExist:
            raise GraphQLError("Content type does not exist.")


# Define Mutations for Creating and Deleting Tags
class CreateTag(graphene.Mutation):
    class Arguments:
        content_type_id = graphene.Int(required=True)  # ID of the ContentType
        object_id = UUID(required=True)  # ID of the object to tag
        tagged_user_id = graphene.Int(required=True)  # ID of the user being tagged

    tag = graphene.Field(TaggedItemType)

    def mutate(self, info, content_type_id, object_id, tagged_user_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to create a tag.")

        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            raise GraphQLError("Invalid content type.")

        try:
            tagged_user = User.objects.get(id=tagged_user_id)
        except User.DoesNotExist:
            raise GraphQLError("User to be tagged not found.")

        # Ensure unique constraint for content_type, object_id, and tagged_user
        if TaggedItem.objects.filter(content_type=content_type, object_id=object_id, tagged_user=tagged_user).exists():
            raise GraphQLError("This user has already been tagged in this content.")

        # Create the tag
        tag = TaggedItem.objects.create(
            content_type=content_type,
            object_id=object_id,
            tagged_user=tagged_user,
            tagged_by=user
        )
        return CreateTag(tag=tag)


class DeleteTag(graphene.Mutation):
    class Arguments:
        tag_id = graphene.UUID(required=True)  # ID of the tag to delete

    success = graphene.Boolean()

    def mutate(self, info, tag_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to delete a tag.")

        try:
            tag = TaggedItem.objects.get(id=tag_id, tagged_by=user)
            tag.delete()
            return DeleteTag(success=True)
        except TaggedItem.DoesNotExist:
            raise GraphQLError("Tag not found or permission denied.")


# Mutation Class to Group All Mutations for Tagged Items
class Mutation(graphene.ObjectType):
    create_tag = CreateTag.Field()
    delete_tag = DeleteTag.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
