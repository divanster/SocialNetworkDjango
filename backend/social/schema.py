import graphene
from graphene_django.types import DjangoObjectType
from .models import Post, PostImage, Rating
from django.contrib.auth import get_user_model
from graphql import GraphQLError

User = get_user_model()


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

    average_rating = graphene.Float()

    def resolve_average_rating(self, info):
        return self.average_rating


class PostImageType(DjangoObjectType):
    class Meta:
        model = PostImage
        fields = "__all__"


class RatingType(DjangoObjectType):
    class Meta:
        model = Rating
        fields = "__all__"


# Define Queries
class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, post_id=graphene.UUID(required=True))
    posts_by_user = graphene.List(PostType, user_id=graphene.Int(required=True))

    def resolve_all_posts(self, info, **kwargs):
        user = info.context.user
        return Post.objects.visible_to_user(user)

    def resolve_post_by_id(self, info, post_id):
        try:
            user = info.context.user
            return Post.objects.visible_to_user(user).get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or you do not have permission to view it.")

    def resolve_posts_by_user(self, info, user_id):
        user = info.context.user
        if user.id != user_id and not user.is_staff:
            raise GraphQLError("Permission denied. You can only view your own posts.")
        return Post.objects.filter(author_id=user_id)


# Define Mutations
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


class UpdatePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.UUID(required=True)
        title = graphene.String()
        content = graphene.String()
        visibility = graphene.String()

    post = graphene.Field(PostType)

    def mutate(self, info, post_id, title=None, content=None, visibility=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to update a post.")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found.")

        if post.author != user:
            raise GraphQLError("You can only update your own posts.")

        if title:
            post.title = title
        if content:
            post.content = content
        if visibility:
            post.visibility = visibility

        post.save()
        return UpdatePost(post=post)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    create_rating = CreateRating.Field()
    update_post = UpdatePost.Field()  # Add updatePost mutation


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
