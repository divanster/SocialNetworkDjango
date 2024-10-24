# backend/albums/serializers.py
from rest_framework import serializers
from albums.album_models import Album  # Import Album from album_models
from albums.photo_models import Photo  # Import Photo from photo_models
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class PhotoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)  # MongoEngine uses ObjectId which can be represented as a string.

    class Meta:
        model = Photo
        fields = ['id', 'album', 'image', 'description', 'created_at']
        read_only_fields = ['id', 'album', 'created_at']


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photos_upload = PhotoSerializer(many=True, write_only=True, required=False)
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Album
        fields = [
            'id', 'user_id', 'title', 'description', 'created_at', 'updated_at',
            'photos', 'photos_upload', 'tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at', 'tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        photos_data = validated_data.pop('photos_upload', [])
        album = Album(**validated_data)
        album.save()  # Save using the default connection to MongoDB

        # Create tagged items for the new album
        self.create_tagged_items(album, tagged_user_ids)

        # Create photos for the album
        for photo_data in photos_data:
            photo = Photo(album=album, **photo_data)
            photo.save()

        return album

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        photos_data = validated_data.pop('photos_upload', [])
        album = super().update(instance, validated_data)

        if tagged_user_ids is not None:
            # Remove all existing tags
            instance.tags.all().delete()
            # Recreate tags with the provided user IDs
            self.create_tagged_items(album, tagged_user_ids)

        # Update existing photos or add new ones
        existing_photos = {str(photo.id): photo for photo in instance.get_photos()}

        for photo_data in photos_data:
            photo_id = photo_data.get('id')
            if photo_id and photo_id in existing_photos:
                # Update existing photo
                photo = existing_photos[photo_id]
                photo.image = photo_data.get('image', photo.image)
                photo.description = photo_data.get('description', photo.description)
                photo.save()
            elif not photo_id:
                # Create new photo
                new_photo = Photo(album=album, **photo_data)
                new_photo.save()

        # Delete photos that were not included in the update request
        existing_photo_ids = set(existing_photos.keys())
        updated_photo_ids = {photo_data.get('id') for photo_data in photos_data if photo_data.get('id')}
        photos_to_delete = existing_photo_ids - updated_photo_ids

        for photo_id in photos_to_delete:
            existing_photos[photo_id].delete()

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
                continue  # Ignore if user does not exist
