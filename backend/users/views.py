import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer
from rest_framework.generics import CreateAPIView

# Get an instance of a logger
logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("id", type="UUID", description="UUID of the profile")
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific user profile by UUID.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns the profile of the authenticated user.
        """
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Ensures the user is associated with the profile during update.
        """
        serializer.save(user=self.request.user)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom user data.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("id", type="UUID", description="UUID of the user")]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific user by UUID.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns the authenticated user's data.
        """
        return CustomUser.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Handles the `me` endpoint for the authenticated user.
        Supports `GET`, `PUT`, and `PATCH` methods.
        """
        if request.method in ['PUT', 'PATCH']:
            # Update the user's profile
            serializer = self.get_serializer(request.user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            # Retrieve the user's profile
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)


class CustomUserSignupView(CreateAPIView):
    """
    API view for signing up new users.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        """
        Handles user creation. Logs the request data and handles errors.
        """
        logger.debug(f"Received signup request data: {request.data}")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.debug(f"User created successfully: {user}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}")
                return Response({"detail": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Signup validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
