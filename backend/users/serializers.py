# users/serializers.py

from rest_framework import serializers
from tagging.serializers import TaggedItemSerializer
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from tagging.models import TaggedItem

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    tagged_user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'),
        write_only=True,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'profile_picture', 'bio', 'phone', 'town', 'country',
            'relationship_status', 'tags', 'tagged_user_ids'
        ]
        read_only_fields = ['tags']


    def update(self, instance, validated_data):
        tagged_user_ids = validated_data.pop('tagged_user_ids', None)
        profile = super().update(instance, validated_data)
        if tagged_user_ids is not None:
            instance.tags.all().delete()
            self.create_tagged_items(profile, tagged_user_ids)
        return profile

    def create_tagged_items(self, profile, tagged_user_ids):
        for user_id in tagged_user_ids:
            TaggedItem.objects.create(
                content_object=profile,
                tagged_user_id=user_id,
                tagged_by=self.context['request'].user
            )

    @extend_schema_field(TaggedItemSerializer(many=True))
    def get_tags(self, instance) -> list:
        return TaggedItemSerializer(instance.tags.all(), many=True).data


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'password2', 'profile'
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
        Ensure that both passwords match.
        """
        password = data.get('password')
        password2 = data.get('password2')

        if password or password2:
            if password != password2:
                raise ValidationError({"non_field_errors": ["Passwords do not match."]})
        return data

    def create(self, validated_data):
        """
        Create a new user instance after removing password2.
        """
        profile_data = validated_data.pop('profile', {})
        with transaction.atomic():
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username']
            )
            if 'password' in validated_data:
                user.set_password(validated_data['password'])
            user.save()

            if profile_data:
                # Retrieve the existing profile created by signals
                profile = user.profile
                profile_serializer = UserProfileSerializer(
                    profile,
                    data=profile_data,
                    partial=True,
                    context={'request': self.context.get('request')}
                )
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()

        return user

    def update(self, instance, validated_data):
        """
        Update user instance and associated profile.
        """
        profile_data = validated_data.pop('profile', {})
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        if profile_data:
            profile_serializer = UserProfileSerializer(
                instance.profile,
                data=profile_data,
                partial=True,
                context={'request': self.context.get('request')}
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        return instance

    def get_serializer_context(self):
        """
        Ensure the request is passed in the context for nested serializers.
        """
        context = super().get_serializer_context()
        context.update({'request': self.context.get('request')})
        return context
