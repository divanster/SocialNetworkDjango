import graphene
from graphene_django.types import DjangoObjectType
from .models import Post, PostImage, Rating
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphene import UUID

# Get the custom User model
User = get_user_model()


# Define GraphQL Types for Post, PostImage, and Rating models
class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"  # Expose all fields of the model

    average_rating = graphene.Float()

    def resolve_average_rating(self, info):
        return self.average_rating


class PostImageType(DjangoObjectType):
    class Meta:
        model = PostImage
        fields = "__all__"  # Expose all fields of the model


class RatingType(DjangoObjectType):
    class Meta:
        model = Rating
        fields = "__all__"  # Expose all fields of the model


# Define Queries for Posts, Images, and Ratings
class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, post_id=graphene.UUID(required=True))
    posts_by_user = graphene.List(PostType, user_id=graphene.Int(required=True))
    post_images = graphene.List(PostImageType, post_id=graphene.UUID(required=True))
    post_ratings = graphene.List(RatingType, post_id=graphene.UUID(required=True))

    # Resolve all posts visible to the logged-in user
    def resolve_all_posts(self, info, **kwargs):
        user = info.context.user
        return Post.objects.visible_to_user(user)

    # Resolve a specific post by its ID
    def resolve_post_by_id(self, info, post_id):
        try:
            user = info.context.user
            return Post.objects.visible_to_user(user).get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError(
                "Post not found or you do not have permission to view it.")

    # Resolve posts created by a specific user
    def resolve_posts_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own posts.")
        return Post.objects.filter(author_id=user_id)

    # Resolve images for a specific post
    def resolve_post_images(self, info, post_id):
        try:
            post = Post.objects.get(id=post_id)
            return post.images.all()
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

    # Resolve ratings for a specific post
    def resolve_post_ratings(self, info, post_id):
        try:
            post = Post.objects.get(id=post_id)
            return post.ratings.all()
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")


# Define Mutations for Creating Posts, Images, and Ratings
class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String()
        visibility = graphene.String(default_value="public")

    post = graphene.Field(PostType)

    def mutate(self, info, title, content=None, visibility="public"):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to create a post.")

        post = Post.objects.create(
            author=user,
            title=title,
            content=content,
            visibility=visibility
        )
        return CreatePost(post=post)


class CreateRating(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)
        value = graphene.Int(required=True)

    rating = graphene.Field(RatingType)

    def mutate(self, info, post_id, value):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to rate a post.")

        if value < 1 or value > 5:
            raise GraphQLError("Rating value must be between 1 and 5.")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

        if Rating.objects.filter(post=post, user=user).exists():
            raise GraphQLError("You have already rated this post.")

        rating = Rating.objects.create(post=post, user=user, value=value)
        return CreateRating(rating=rating)


# Mutation Class to Group All Mutations for Social
class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    create_rating = CreateRating.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
