# backend/albums/serializers.py
from rest_framework import serializers
from .models import Album, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'album', 'image', 'description', 'created_at']
        read_only_fields = ['id', 'album', 'created_at']


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'user', 'title', 'description', 'created_at', 'updated_at', 'photos']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
