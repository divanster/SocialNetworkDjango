from rest_framework import serializers
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.db import transaction


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile, including basic information and profile picture.
    """

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'profile_picture', 'bio', 'phone', 'town', 'country',
            'relationship_status'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser, incorporating nested UserProfile data and validation.
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)
    bio = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    town = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    relationship_status = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False,
                                     validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'gender', 'date_of_birth', 'bio', 'phone',
            'town', 'country', 'relationship_status', 'profile_picture'
        ]
        extra_kwargs = {
            'email': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]
            },
            'username': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]
            },
        }

    def validate(self, data):
        """
        Validate password confirmation and organize profile data.
        """
        profile_fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'bio', 'phone', 'town', 'country', 'relationship_status',
            'profile_picture'
        ]

        profile_data = {field: data.pop(field) for field in profile_fields if
                        field in data}
        data['profile'] = profile_data

        # Validate passwords
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        """
        Create a new user and associated UserProfile.
        """
        profile_data = validated_data.pop('profile', {})
        profile_picture = profile_data.pop('profile_picture', None)

        with transaction.atomic():
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username']
            )
            if 'password' in validated_data:
                user.set_password(validated_data['password'])
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            for key, value in profile_data.items():
                setattr(profile, key, value)

            if profile_picture:
                profile.profile_picture = profile_picture

            profile.save()

        return user

    def update(self, instance, validated_data):
        """
        Update the user and associated UserProfile.
        """
        profile_data = validated_data.pop('profile', {})
        profile_picture = profile_data.pop('profile_picture', None)

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        # Update or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for key, value in profile_data.items():
            setattr(profile, key, value)

        if profile_picture:
            profile.profile_picture = profile_picture

        profile.save()

        return instance
