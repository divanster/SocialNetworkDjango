# backend/albums/serializers.py

from rest_framework import serializers
from .models import Album, Photo
from tagging.serializers import TaggedItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'album', 'image', 'description', 'created_at']
        read_only_fields = ['id', 'album', 'created_at']


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photos_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
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
            Photo.objects.create(album=album, image=photo_data)
        return album

    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        photos_data = validated_data.pop('photos_upload', [])
        album = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            # Remove existing tags and add new ones
            instance.tags.all().delete()
            self.create_tagged_items(album, tagged_user_ids)
        for photo_data in photos_data:
            Photo.objects.create(album=album, image=photo_data)
        return album

    def create_tagged_items(self, album, tagged_user_ids):
        from tagging.models import TaggedItem
        for user_id in tagged_user_ids:
            TaggedItem.objects.create(
                content_object=album,
                tagged_user_id=user_id,
                tagged_by=self.context['request'].user
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.context['request']})
        return context
