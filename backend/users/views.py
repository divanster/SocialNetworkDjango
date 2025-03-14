# backend/users/views.py

from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, authentication_classes, \
    permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import CustomUser, UserProfile
from .serializers import CustomUserSerializer, UserProfileSerializer, \
    TokenRefreshSerializer
from rest_framework.generics import CreateAPIView
from kafka_app.tasks import send_welcome_email, send_profile_update_notification
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache

import logging

# Initialize logger once at the top
logger = logging.getLogger('users')


class CustomTokenRefreshView(generics.GenericAPIView):
    """
    Custom view to refresh the access token using the provided refresh token.
    """
    serializer_class = TokenRefreshSerializer  # Declare the serializer_class here
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        summary="Refresh JWT Token",
        description="Refreshes the JWT access token using the provided refresh token.",
        request=TokenRefreshSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    @ratelimit(key='ip', rate='5/m', block=True)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get('refresh')

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info(f"Token refresh successful for user with refresh token.")
            return Response({'access': new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            return Response({'error': f'Invalid token: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

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

    def destroy(self, request, *args, **kwargs):
        """
        Performs a soft delete of the user profile.
        """
        instance = self.get_object()
        instance.delete()  # Soft delete
        logger.info(f"Soft-deleted UserProfile with ID: {instance.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='restore',
            permission_classes=[IsAuthenticated])
    def restore(self, request, pk=None):
        """
        Restores a soft-deleted user profile.
        """
        try:
            profile = UserProfile.all_objects.get(pk=pk, is_deleted=True)
            profile.restore()
            serializer = self.get_serializer(profile)
            logger.info(f"Restored UserProfile with ID: {profile.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            logger.error(f"UserProfile with ID {pk} does not exist or is not deleted.")
            return Response({"detail": "UserProfile not found or not deleted."},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get online users",
    description="Retrieves list of currently online users",
    responses={200: CustomUserSerializer(many=True)}
)
def get_online_users(request):
    # Log the Authorization header received
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    logger.info(f"Authorization header received: {auth_header}")

    online_user_ids = cache.get('online_users', [])
    logger.debug(f"Online User IDs from cache: {online_user_ids}")
    users = CustomUser.objects.filter(id__in=online_user_ids)
    return Response(CustomUserSerializer(users, many=True).data)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom user data.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    @extend_schema(
        summary="List all users",
        description="Retrieves a list of all users in the system.",
        responses={200: CustomUserSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieves the list of users.
        """
        queryset = self.get_queryset()  # This will get all users
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='pk',
                description='UUID of the user',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ],
        summary="Retrieve a specific user",
        description="Retrieves details of a user by their UUID.",
        responses={200: CustomUserSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific user by UUID.
        """
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Performs a soft delete of the user.
        """
        instance = self.get_object()
        instance.delete()  # Soft delete
        logger.info(f"Soft-deleted CustomUser with ID: {instance.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(request.user, data=request.data,
                                             partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
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

    @ratelimit(key='ip', rate='3/h', block=True)
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
                    logger.info(f"User created successfully: {user.email}")
                    send_welcome_email.delay(user.id)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}")
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Signup validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
