import graphene
from graphene_django.types import DjangoObjectType
from .models import Album, Photo
from tagging.models import TaggedItem


# Define GraphQL Types for Album and Photo models
class AlbumType(DjangoObjectType):
    class Meta:
        model = Album
        fields = "__all__"  # Expose all fields of the model

    # Define custom field to get related photos
    photos = graphene.List(lambda: PhotoType)

    def resolve_photos(self, info):
        return self.get_photos()


class PhotoType(DjangoObjectType):
    class Meta:
        model = Photo
        fields = "__all__"  # Expose all fields of the model

    # Define custom field to get image URL
    image_url = graphene.String()

    def resolve_image_url(self, info):
        return self.get_image_url()


# Define Queries for Albums and Photos
class Query(graphene.ObjectType):
    all_albums = graphene.List(AlbumType)
    album_by_id = graphene.Field(AlbumType, id=graphene.UUID(required=True))
    all_photos = graphene.List(PhotoType)
    photo_by_id = graphene.Field(PhotoType, id=graphene.UUID(required=True))

    # Resolve all albums visible to the current user
    def resolve_all_albums(self, info, **kwargs):
        user = info.context.user
        return Album.objects.visible_to_user(user)

    # Resolve a specific album by its ID
    def resolve_album_by_id(self, info, id):
        try:
            user = info.context.user
            return Album.objects.visible_to_user(user).get(id=id)
        except Album.DoesNotExist:
            return None

    # Resolve all photos visible to the current user
    def resolve_all_photos(self, info, **kwargs):
        user = info.context.user
        return Photo.objects.visible_to_user(user)

    # Resolve a specific photo by its ID
    def resolve_photo_by_id(self, info, id):
        try:
            user = info.context.user
            return Photo.objects.visible_to_user(user).get(id=id)
        except Photo.DoesNotExist:
            return None


# Define Mutations for Creating Albums and Photos
class CreateAlbum(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        visibility = graphene.String()  # Visibility can be PUBLIC, PRIVATE, FRIENDS

    album = graphene.Field(AlbumType)

    def mutate(self, info, title, description=None, visibility='PUBLIC'):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to create an album.")

        album = Album.objects.create(
            user=user,
            title=title,
            description=description,
            visibility=visibility
        )
        return CreateAlbum(album=album)


class CreatePhoto(graphene.Mutation):
    class Arguments:
        album_id = graphene.UUID(required=True)
        description = graphene.String()
        image = graphene.String(
            required=True)  # For simplicity, assuming URL as string input

    photo = graphene.Field(PhotoType)

    def mutate(self, info, album_id, description=None, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to add a photo.")

        try:
            album = Album.objects.visible_to_user(user).get(id=album_id)
        except Album.DoesNotExist:
            raise Exception("Album not found or access denied.")

        photo = Photo.objects.create(
            album=album,
            description=description,
            image=image  # Note: In practice, handle image uploads properly
        )
        return CreatePhoto(photo=photo)


# Mutation Class to Group All Mutations for Albums and Photos
class Mutation(graphene.ObjectType):
    create_album = CreateAlbum.Field()
    create_photo = CreatePhoto.Field()


# Create the schema combining Query and Mutation
schema = graphene.Schema(query=Query, mutation=Mutation)
