from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'profile_picture', 'bio', 'phone', 'town',
                  'country', 'relationship_status']


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password', 'profile'
        ]
        extra_kwargs = {
            'email': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]},
            'username': {'validators': [UniqueValidator(queryset=CustomUser.objects.all())]}
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()

        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('last_name', profile.last_name)
        profile.gender = profile_data.get('gender', profile.gender)
        profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
        profile.profile_picture = profile_data.get('profile_picture', profile.profile_picture)
        profile.bio = profile_data.get('bio', profile.bio)
        profile.phone = profile_data.get('phone', profile.phone)
        profile.town = profile_data.get('town', profile.town)
        profile.country = profile_data.get('country', profile.country)
        profile.relationship_status = profile_data.get('relationship_status', profile.relationship_status)
        profile.save()

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
            instance.save()

        return instance
