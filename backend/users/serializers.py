# serializers.py
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'profile_picture', 'bio', 'phone', 'town', 'country',
            'relationship_status'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password', 'profile'
        ]
        extra_kwargs = {
            'email': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
            'username': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all())]}
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        try:
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()
            if profile_data:
                UserProfile.objects.create(user=user, **profile_data)
            return user
        except Exception as e:
            raise ValidationError(
                f"An error occurred while creating the user: {str(e)}")

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        try:
            instance.email = validated_data.get('email', instance.email)
            instance.username = validated_data.get('username', instance.username)
            instance.save()

            if profile_data:
                profile = instance.profile
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()

            if 'password' in validated_data:
                instance.set_password(validated_data['password'])
                instance.save()

            return instance
        except Exception as e:
            raise ValidationError(
                f"An error occurred while updating the user: {str(e)}")
