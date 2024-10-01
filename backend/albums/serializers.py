from rest_framework import serializers
from .models import Album, Photo
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class PhotoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # Allow sending ID for update

    class Meta:
        model = Photo
        fields = ['id', 'album', 'image', 'description', 'created_at']
        read_only_fields = ['id', 'album', 'created_at']


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photos_upload = serializers.ListField(
        child=PhotoSerializer(),  # Modified to use PhotoSerializer for consistency
        write_only=True,
        required=False
    )
    tags = TaggedItemSerializer(many=True, read_only=True)
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = Album
        fields = [
            'id', 'user', 'title', 'description', 'created_at', 'updated_at',
            'photos', 'photos_upload', 'tags', 'tagged_user_ids'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'tags']

    def create(self, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', [])
        photos_data = validated_data.pop('photos_upload', [])
        album = Album.objects.create(**validated_data)
        self.create_tagged_items(album, tagged_user_ids)
        for photo_data in photos_data:
            Photo.objects.create(album=album, **photo_data)
        return album

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        photos_data = validated_data.pop('photos_upload', [])
        album = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(album, tagged_user_ids)

        # Handle photo updates and deletions
        existing_photos = {photo.id: photo for photo in instance.photos.all()}
        for photo_data in photos_data:
            photo_id = photo_data.get('id')
            if photo_id and photo_id in existing_photos:
                photo = existing_photos[photo_id]
                photo.image = photo_data.get('image', photo.image)
                photo.description = photo_data.get('description', photo.description)
                photo.save()
            elif photo_id is None:
                Photo.objects.create(album=album, **photo_data)

        # Delete photos not included in the update
        existing_photo_ids = set(existing_photos.keys())
        updated_photo_ids = set(
            photo_data.get('id') for photo_data in photos_data if 'id' in photo_data)
        Photo.objects.filter(album=album,
                             id__in=(existing_photo_ids - updated_photo_ids)).delete()

        return album

    def create_tagged_items(self, album, tagged_user_ids):
        from tagging.models import TaggedItem
        for user_id in tagged_user_ids:
            TaggedItem.objects.create(
                content_object=album,
                tagged_user_id=user_id,
                tagged_by=self.context['request'].user
            )
