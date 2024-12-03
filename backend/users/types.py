# users/types.py
from graphene_django.types import DjangoObjectType
from .models import UserProfile


class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = "__all__"
