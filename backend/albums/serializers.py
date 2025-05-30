# backend/albums/serializers.py

import logging
from rest_framework import serializers
from albums.models import Album, Photo
from tagging.serializers import TaggedItemSerializer  # Ensure this serializer exists
from django.contrib.auth import get_user_model
from core.choices import VisibilityChoices
from rest_framework.exceptions import ValidationError  # Import ValidationError

from users.serializers import CustomUserSerializer  # Import CustomUserSerializer

User = get_user_model()

logger = logging.getLogger(__name__)


class PhotoSerializer(serializers.ModelSerializer):
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )
    tags = TaggedItemSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = ['id', 'album', 'image', 'description', 'created_at', 'tags',
                  'tagged_user_ids']
        read_only_fields = ['id', 'created_at', 'tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        album = validated_data['album']

        # Ensure the user can add photos to this album
        if self.context['request'].user != album.user:
            raise serializers.ValidationError(
                "You do not have permission to add photos to this album.")

        photo = Photo.objects.create(**validated_data)

        # Create tagged items for the new photo
        self.create_tagged_items(photo, tagged_user_ids)

        return photo

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)

        # Ensure the user can update this photo
        if self.context['request'].user != instance.album.user:
            raise serializers.ValidationError(
                "You do not have permission to edit this photo.")

        photo = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            # Remove all existing tags
            instance.tags.all().delete()
            # Recreate tags with the provided user IDs
            self.create_tagged_items(photo, tagged_user_ids)

        return photo

    def create_tagged_items(self, photo, tagged_user_ids):
        from tagging.models import TaggedItem

        tagged_by = self.context['request'].user
        for user_id in tagged_user_ids:
            try:
                TaggedItem.objects.create(
                    content_object=photo,
                    tagged_user_id=user_id,
                    tagged_by=tagged_by
                )
            except User.DoesNotExist:
                logger.warning(f"User with ID {user_id} does not exist. Skipping tagging.")
                continue  # Ignore if user does not exist


class AlbumSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(source='user', read_only=True)  # Use CustomUserSerializer
    photos = PhotoSerializer(many=True, read_only=True)
    photos_upload = PhotoSerializer(many=True, write_only=True, required=False)
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )
    visibility = serializers.ChoiceField(choices=VisibilityChoices.choices)

    class Meta:
        model = Album
        fields = [
            'id', 'user_id', 'author', 'title', 'description', 'visibility', 'created_at',
            'updated_at',
            'photos', 'photos_upload', 'tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at', 'tags', 'author']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        photos_data = validated_data.pop('photos_upload', [])
        album = Album.objects.create(**validated_data)

        # Create tagged items for the new album
        self.create_tagged_items(album, tagged_user_ids)

        # Create photos for the album
        for photo_data in photos_data:
            photo_serializer = PhotoSerializer(data=photo_data, context=self.context)
            if photo_serializer.is_valid():
                photo_serializer.save(album=album)
            else:
                raise serializers.ValidationError(photo_serializer.errors)

        return album

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        photos_data = validated_data.pop('photos_upload', [])

        # Ensure the user can update this album
        if self.context['request'].user != instance.user:
            raise serializers.ValidationError(
                "You do not have permission to edit this album.")

        album = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            # Remove all existing tags
            instance.tags.all().delete()
            # Recreate tags with the provided user IDs
            self.create_tagged_items(album, tagged_user_ids)

        # Update existing photos or add new ones
        existing_photos = {str(photo.id): photo for photo in instance.photos.all()}

        for photo_data in photos_data:
            photo_id = photo_data.get('id')
            if photo_id and photo_id in existing_photos:
                # Update existing photo
                photo_serializer = PhotoSerializer(
                    existing_photos[photo_id],
                    data=photo_data,
                    partial=True,
                    context=self.context
                )
                if photo_serializer.is_valid():
                    photo_serializer.save()
                else:
                    raise serializers.ValidationError(photo_serializer.errors)
            elif not photo_id:
                # Create new photo
                photo_serializer = PhotoSerializer(data=photo_data,
                                                   context=self.context)
                if photo_serializer.is_valid():
                    photo_serializer.save(album=album)
                else:
                    raise serializers.ValidationError(photo_serializer.errors)

        return album

    def create_tagged_items(self, album, tagged_user_ids):
        from tagging.models import TaggedItem

        tagged_by = self.context['request'].user
        for user_id in tagged_user_ids:
            try:
                TaggedItem.objects.create(
                    content_object=album,
                    tagged_user_id=user_id,
                    tagged_by=tagged_by
                )
            except User.DoesNotExist:
                logger.warning(f"User with ID {user_id} does not exist. Skipping tagging.")
                continue  # Ignore if user does not exist
