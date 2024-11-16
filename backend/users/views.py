# backend/users/test_views.py

import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer
from rest_framework.generics import CreateAPIView
from users.tasks import send_welcome_email, send_profile_update_notification  # Import tasks
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError



# Initialize logger once at the top
logger = logging.getLogger('users')


class TokenRefreshView(APIView):
    """
    Custom view to refresh the access token using the provided refresh token.
    """

    def post(self, request):
        refresh_token = request.data.get('refresh', None)

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info(f"Token refresh successful for refresh token: {refresh_token}")
            return Response({'access': new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:  # Catch token-specific errors
            return Response({'error': f'Invalid token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  # Changed from 'id' to 'pk'
    lookup_url_kwarg = 'pk'  # Changed from 'id' to 'pk'

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='pk',
                description='UUID of the user profile',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific user profile by UUID.
        """
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Ensures the user is associated with the profile during update and sends notification.
        """
        profile = serializer.save(user=self.request.user)
        # Trigger the task to send profile update notification
        send_profile_update_notification.delay(profile.user.id)
        logger.info(f"Profile updated for user {profile.user.id}, notification task scheduled.")


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom user data.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'  # Changed from 'id' to 'pk'
    lookup_url_kwarg = 'pk'  # Changed from 'id' to 'pk'

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='pk',
                description='UUID of the user',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific user by UUID.
        """
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get', 'put', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """
        Handles the `me` endpoint for the authenticated user.
        Supports `GET`, `PUT`, and `PATCH` methods.
        """
        if request.method in ['PUT', 'PATCH']:
            # Determine if the update is partial
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Log and provide feedback for updating the user
            logger.info(f"User data updated for user {request.user.id}")
        else:
            serializer = self.get_serializer(request.user)

        return Response(serializer.data)


class CustomUserSignupView(CreateAPIView):
    """
    API view for signing up new users.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        """
        Handles user creation and sends a welcome email.
        """
        logger.debug(f"Received signup request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.debug(f"User created successfully: {user}")
                    # Trigger the task to send a welcome email asynchronously
                    send_welcome_email.delay(user.id)
                    logger.info(f"Scheduled task to send welcome email to user {user.id}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}")
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            logger.error(f"Signup validation failed: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
