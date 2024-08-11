from rest_framework import serializers
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.db import transaction

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'profile_picture', 'bio', 'phone', 'town', 'country',
            'relationship_status'
        ]

class CustomUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name', required=False)
    last_name = serializers.CharField(source='profile.last_name', required=False)
    gender = serializers.CharField(source='profile.gender', required=False)
    date_of_birth = serializers.DateField(source='profile.date_of_birth', required=False)
    bio = serializers.CharField(source='profile.bio', required=False)
    phone = serializers.CharField(source='profile.phone', required=False)
    town = serializers.CharField(source='profile.town', required=False)
    country = serializers.CharField(source='profile.country', required=False)
    relationship_status = serializers.CharField(source='profile.relationship_status', required=False)

    profile_picture = serializers.ImageField(source='profile.profile_picture', required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'gender', 'date_of_birth', 'bio', 'phone',
            'town', 'country', 'relationship_status', 'profile_picture'
        ]
        extra_kwargs = {
            'email': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
            'username': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
        }

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
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

            UserProfile.objects.create(user=user, profile_picture=profile_picture, **profile_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile_picture = profile_data.pop('profile_picture', None)

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()

        if hasattr(instance, 'profile'):
            for key, value in profile_data.items():
                setattr(instance.profile, key, value)
            if profile_picture:
                instance.profile.profile_picture = profile_picture
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance, profile_picture=profile_picture, **profile_data)

        return instance
