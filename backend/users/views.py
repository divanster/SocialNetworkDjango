

# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]  # Allow registration without authentication

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
