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
    # Directly use fields without 'source' mapping
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
        # Collect profile data into a dictionary
        profile_fields = ['first_name', 'last_name', 'gender', 'date_of_birth',
                          'bio', 'phone', 'town', 'country', 'relationship_status',
                          'profile_picture']

        profile_data = {}
        for field in profile_fields:
            if field in data:
                profile_data[field] = data.pop(field)

        data['profile'] = profile_data  # Ensure profile key exists in validated_data

        # Validate passwords
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile_picture = profile_data.pop('profile_picture', None)

        print(f"Debug: Profile data received: {profile_data}")  # Debug output

        with transaction.atomic():
            # Create the user
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username']
            )
            if 'password' in validated_data:
                user.set_password(validated_data['password'])
            user.save()

            # Create or update the UserProfile instance explicitly
            profile, created = UserProfile.objects.get_or_create(user=user)
            print(f"Debug: Created = {created}, Profile = {profile}")  # Debug output

            for key, value in profile_data.items():
                setattr(profile, key, value)
                print(f"Debug: Setting {key} to {value}")  # Debug output

            if profile_picture:
                profile.profile_picture = profile_picture
                print("Debug: Setting profile picture")  # Debug output

            profile.save()
            print(f"Debug: Profile saved with data: {profile.__dict__}")  # Debug output

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
            UserProfile.objects.create(user=instance, profile_picture=profile_picture,
                                       **profile_data)

        return instance
