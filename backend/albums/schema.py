# backend/albums/schema.py

import logging
import graphene
from graphene_django.types import DjangoObjectType
from .models import Album, Photo
from tagging.models import TaggedItem
from core.choices import VisibilityChoices  # Ensure this is correctly defined in core/choices.py
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphql_jwt.decorators import login_required, staff_member_required

logger = logging.getLogger(__name__)

User = get_user_model()


# Define GraphQL Types for Album and Photo models
class PhotoType(DjangoObjectType):
    class Meta:
        model = Photo
        fields = "__all__"  # Expose all fields of the model

    # Define custom field to get image URL
    image_url = graphene.String()

    def resolve_image_url(self, info):
        return self.get_image_url()


class AlbumType(DjangoObjectType):
    class Meta:
        model = Album
        fields = "__all__"  # Expose all fields of the model

    # Define custom field to get related photos
    photos = graphene.List(lambda: PhotoType)

    def resolve_photos(self, info):
        return self.get_photos()


# Define Visibility Enum for GraphQL
class VisibilityEnum(graphene.Enum):
    PUBLIC = 'public'
    FRIENDS = 'friends'
    PRIVATE = 'private'


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
            raise GraphQLError("Album not found or you do not have permission to view it.")

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
            raise GraphQLError("Photo not found or you do not have permission to view it.")


# Define Mutations for Creating Albums and Photos
class CreateAlbum(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        visibility = VisibilityEnum(default_value=VisibilityChoices.PUBLIC)

    album = graphene.Field(AlbumType)

    @login_required
    def mutate(self, info, title, description=None, visibility='public'):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to create an album.")

        album = Album.objects.create(
            user=user,
            title=title,
            description=description,
            visibility=visibility
        )
        logger.info(f"Album with ID {album.id} created by user {user.id}")
        return CreateAlbum(album=album)


class CreatePhoto(graphene.Mutation):
    class Arguments:
        album_id = graphene.UUID(required=True)
        description = graphene.String()
        image = graphene.String(required=True)  # For simplicity, assuming URL as string input

    photo = graphene.Field(PhotoType)

    @login_required
    def mutate(self, info, album_id, description=None, image=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required to add a photo.")

        try:
            album = Album.objects.visible_to_user(user).get(id=album_id)
        except Album.DoesNotExist:
            raise GraphQLError("Album not found or access denied.")

        photo = Photo.objects.create(
            album=album,
            description=description,
            image=image  # Note: In practice, handle image uploads properly using GraphQL Uploads
        )
        logger.info(f"Photo with ID {photo.id} created in album {album.id} by user {user.id}")
        return CreatePhoto(photo=photo)


# Define Mutations for Updating, Deleting, and Restoring Albums and Photos
class UpdateAlbum(graphene.Mutation):
    class Arguments:
        album_id = graphene.UUID(required=True)
        title = graphene.String()
        description = graphene.String()
        visibility = VisibilityEnum()

    album = graphene.Field(AlbumType)

    @login_required
    def mutate(self, info, album_id, title=None, description=None, visibility=None):
        user = info.context.user
        try:
            album = Album.objects.get(id=album_id, is_deleted=False)
        except Album.DoesNotExist:
            raise GraphQLError("Album not found.")

        if album.user != user:
            raise GraphQLError("You do not have permission to edit this album.")

        if title:
            album.title = title
        if description:
            album.description = description
        if visibility:
            album.visibility = visibility

        album.save()
        logger.info(f"Album with ID {album.id} updated by user {user.id}")
        return UpdateAlbum(album=album)


class DeleteAlbum(graphene.Mutation):
    class Arguments:
        album_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, album_id):
        user = info.context.user
        try:
            album = Album.objects.get(id=album_id, is_deleted=False)
        except Album.DoesNotExist:
            raise GraphQLError("Album not found or already deleted.")

        if album.user != user and not user.is_staff:
            raise GraphQLError("You do not have permission to delete this album.")

        album.delete()  # Soft delete
        logger.info(f"Album with ID {album.id} soft-deleted by user {user.id}")
        return DeleteAlbum(success=True)


class RestoreAlbum(graphene.Mutation):
    class Arguments:
        album_id = graphene.UUID(required=True)

    album = graphene.Field(AlbumType)

    @staff_member_required
    def mutate(self, info, album_id):
        try:
            album = Album.all_objects.get(id=album_id, is_deleted=True)
            album.restore()
            logger.info(f"Album with ID {album.id} restored by admin user {info.context.user.id}")
            return RestoreAlbum(album=album)
        except Album.DoesNotExist:
            raise GraphQLError("Album not found or not deleted.")


class UpdatePhoto(graphene.Mutation):
    class Arguments:
        photo_id = graphene.UUID(required=True)
        description = graphene.String()
        image = graphene.String()  # For simplicity, assuming URL as string input

    photo = graphene.Field(PhotoType)

    @login_required
    def mutate(self, info, photo_id, description=None, image=None):
        user = info.context.user
        try:
            photo = Photo.objects.get(id=photo_id, is_deleted=False)
        except Photo.DoesNotExist:
            raise GraphQLError("Photo not found.")

        if photo.album.user != user:
            raise GraphQLError("You do not have permission to edit this photo.")

        if description:
            photo.description = description
        if image:
            photo.image = image  # Note: Handle image uploads appropriately

        photo.save()
        logger.info(f"Photo with ID {photo.id} updated by user {user.id}")
        return UpdatePhoto(photo=photo)


class DeletePhoto(graphene.Mutation):
    class Arguments:
        photo_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, photo_id):
        user = info.context.user
        try:
            photo = Photo.objects.get(id=photo_id, is_deleted=False)
        except Photo.DoesNotExist:
            raise GraphQLError("Photo not found or already deleted.")

        if photo.album.user != user and not user.is_staff:
            raise GraphQLError("You do not have permission to delete this photo.")

        photo.delete()  # Soft delete
        logger.info(f"Photo with ID {photo.id} soft-deleted by user {user.id}")
        return DeletePhoto(success=True)


class RestorePhoto(graphene.Mutation):
    class Arguments:
        photo_id = graphene.UUID(required=True)

    photo = graphene.Field(PhotoType)

    @staff_member_required
    def mutate(self, info, photo_id):
        try:
            photo = Photo.all_objects.get(id=photo_id, is_deleted=True)
            photo.restore()
            logger.info(f"Photo with ID {photo.id} restored by admin user {info.context.user.id}")
            return RestorePhoto(photo=photo)
        except Photo.DoesNotExist:
            raise GraphQLError("Photo not found or not deleted.")


# Mutation Class to Group All Mutations for Albums and Photos
class Mutation(graphene.ObjectType):
    create_album = CreateAlbum.Field()
    create_photo = CreatePhoto.Field()
    update_album = UpdateAlbum.Field()
    delete_album = DeleteAlbum.Field()
    restore_album = RestoreAlbum.Field()
    update_photo = UpdatePhoto.Field()
    delete_photo = DeletePhoto.Field()
    restore_photo = RestorePhoto.Field()

# **Do NOT define `schema = graphene.Schema(...)` here.**
