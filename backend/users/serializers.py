from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


def validate_username(value):
    """Ensure the username is at least 2 characters long."""
    if len(value) < 2:
        raise serializers.ValidationError("Username must be at least 2 characters long.")
    return value


class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'profile_picture', 'profile_picture_url', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'email': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
            'username': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]}
        }

    @extend_schema_field(serializers.CharField)
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return '/static/images/default_profile.png'

    def validate_first_name(self, value):
        """Ensure the first name is at least 2 characters long."""
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value

    def validate_last_name(self, value):
        """Ensure the last name is at least 2 characters long."""
        if len(value) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        if 'admin' in value.lower():
            raise serializers.ValidationError("Username cannot contain 'admin'.")
        return value

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance
