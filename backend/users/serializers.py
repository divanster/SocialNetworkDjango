from rest_framework import serializers
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.db import transaction


class CustomUserSerializer(serializers.ModelSerializer):
    # Flattened profile fields
    first_name = serializers.CharField(source='profile.first_name', required=False)
    last_name = serializers.CharField(source='profile.last_name', required=False)
    gender = serializers.CharField(source='profile.gender', required=False)
    date_of_birth = serializers.DateField(source='profile.date_of_birth',
                                          required=False)
    bio = serializers.CharField(source='profile.bio', required=False)
    phone = serializers.CharField(source='profile.phone', required=False)
    town = serializers.CharField(source='profile.town', required=False)
    country = serializers.CharField(source='profile.country', required=False)
    relationship_status = serializers.CharField(source='profile.relationship_status',
                                                required=False)

    # Add a separate field for the profile picture upload
    image_file = serializers.ImageField(write_only=True, required=False)

    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'gender', 'date_of_birth', 'bio', 'phone',
            'town', 'country', 'relationship_status', 'image_file'
        ]
        extra_kwargs = {
            'email': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
            'username': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Extracting profile data
        profile_data = {
            'first_name': validated_data.pop('profile.first_name', ''),
            'last_name': validated_data.pop('profile.last_name', ''),
            'gender': validated_data.pop('profile.gender', ''),
            'date_of_birth': validated_data.pop('profile.date_of_birth', None),
            'profile_picture': validated_data.pop('profile.profile_picture', None),
            'bio': validated_data.pop('profile.bio', ''),
            'phone': validated_data.pop('profile.phone', ''),
            'town': validated_data.pop('profile.town', ''),
            'country': validated_data.pop('profile.country', ''),
            'relationship_status': validated_data.pop('profile.relationship_status',
                                                      'S'),
        }

        # Handle the image upload separately
        image_file = validated_data.pop('image_file', None)

        with transaction.atomic():
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()

            # Check if a UserProfile already exists for this user
            if hasattr(user, 'profile'):
                # Update existing profile
                for key, value in profile_data.items():
                    setattr(user.profile, key, value)
                if image_file:
                    user.profile.profile_picture = image_file
                user.profile.save()
            else:
                # Create a new profile
                profile_data['profile_picture'] = image_file
                UserProfile.objects.create(user=user, **profile_data)

        return user
