from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'profile_picture', 'profile_picture_url']

    @extend_schema_field(serializers.CharField)
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return '/static/images/profile_picture.png'
