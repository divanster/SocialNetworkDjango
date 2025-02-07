# backend/social/schema.py

import logging
import graphene
from graphene_django.types import DjangoObjectType
from social.models import Post, PostImage, Rating
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required
from django.core.exceptions import ValidationError

# Initialize logger
logger = logging.getLogger(__name__)

User = get_user_model()


class PostImageType(DjangoObjectType):
    """
    GraphQL Type for PostImage model.
    Excludes soft-deletion fields.
    """
    class Meta:
        model = PostImage
        exclude = ('is_deleted', 'deleted_at')


class RatingType(DjangoObjectType):
    """
    GraphQL Type for Rating model.
    Excludes soft-deletion fields.
    """
    class Meta:
        model = Rating
        exclude = ('is_deleted', 'deleted_at')


class PostType(DjangoObjectType):
    """
    GraphQL Type for Post model.
    Excludes soft-deletion fields and includes average_rating.
    """
    average_rating = graphene.Float()

    class Meta:
        model = Post
        exclude = ('is_deleted', 'deleted_at')

    def resolve_average_rating(self, info):
        return self.average_rating


# Helper function to get authenticated user
def get_authenticated_user(info):
    user = info.context.user
    if user.is_anonymous:
        raise GraphQLError("Authentication required.")
    return user


# Define Queries
class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, post_id=graphene.UUID(required=True))
    posts_by_user = graphene.List(PostType, user_id=graphene.UUID(required=True))

    @login_required
    def resolve_all_posts(self, info, **kwargs):
        user = info.context.user
        return Post.objects.visible_to_user(user)

    def resolve_post_by_id(self, info, post_id):
        user = info.context.user
        try:
            post = Post.objects.visible_to_user(user).get(uuid=post_id)
            return post
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or you do not have permission to view it.")

    def resolve_posts_by_user(self, info, user_id):
        user = info.context.user
        if str(user.id) != str(user_id) and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own posts.")
        return Post.objects.filter(user_id=user_id)


# Define Mutations
class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String()
        visibility = graphene.String(default_value="public")

    post = graphene.Field(PostType)

    @login_required
    def mutate(self, info, title, content=None, visibility="public"):
        user = info.context.user
        post = Post.objects.create(
            user=user,
            title=title,
            content=content,
            visibility=visibility
        )
        logger.info(f"Post with ID {post.id} created by user {user.id}")
        return CreatePost(post=post)


class CreateRating(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)
        value = graphene.Int(required=True)

    rating = graphene.Field(RatingType)

    @login_required
    def mutate(self, info, post_id, value):
        user = info.context.user
        if value < 1 or value > 5:
            raise GraphQLError("Rating value must be between 1 and 5.")

        try:
            post = Post.objects.get(uuid=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

        if post.user == user:
            raise GraphQLError("You cannot rate your own post.")

        if Rating.objects.filter(post=post, user=user, is_deleted=False).exists():
            raise GraphQLError("You have already rated this post.")

        rating = Rating.objects.create(post=post, user=user, value=value)
        logger.info(f"User {user.id} rated post {post.id} with value {value}")
        return CreateRating(rating=rating)


class UpdatePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)
        title = graphene.String()
        content = graphene.String()
        visibility = graphene.String()

    post = graphene.Field(PostType)

    @login_required
    def mutate(self, info, post_id, title=None, content=None, visibility=None):
        user = info.context.user
        try:
            post = Post.objects.get(uuid=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

        if post.user != user:
            raise GraphQLError("You can only update your own posts.")

        if title:
            post.title = title
        if content:
            post.content = content
        if visibility:
            post.visibility = visibility

        post.save()
        logger.info(f"Post with ID {post.id} updated by user {user.id}")
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, post_id):
        user = info.context.user
        try:
            post = Post.objects.get(uuid=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or already deleted.")

        if post.user != user and not user.is_staff:
            raise GraphQLError("You do not have permission to delete this post.")

        post.delete()  # Soft delete
        logger.info(f"Post with ID {post.id} soft-deleted by user {user.id}")
        return DeletePost(success=True)


class RestorePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)

    post = graphene.Field(PostType)

    @staff_member_required
    def mutate(self, info, post_id):
        try:
            post = Post.all_objects.get(uuid=post_id, is_deleted=True)
            post.restore()
            logger.info(f"Post with ID {post.id} restored by admin user {info.context.user.id}")
            return RestorePost(post=post)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or not deleted.")


# Mutation Class to Group All Mutations
class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    create_rating = CreateRating.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    restore_post = RestorePost.Field()


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
