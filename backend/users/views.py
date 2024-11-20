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
from users.tasks import send_welcome_email, send_profile_update_notification
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from django_ratelimit.decorators import ratelimit

# Initialize logger once at the top
logger = logging.getLogger('users')


class CustomTokenRefreshView(APIView):
    """
    Custom view to refresh the access token using the provided refresh token.
    """
    @ratelimit(key='ip', rate='5/m', block=True)
    def post(self, request):
        refresh_token = request.data.get('refresh', None)

        if not refresh_token:
            return Response({'error': 'Refresh token is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info(f"Token refresh successful for user with refresh token: {refresh_token}")
            return Response({'access': new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.warning(f"Token refresh failed: {str(e)}")  # Specific exception logging
            return Response({'error': f'Invalid token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


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

    def update(self, request, *args, **kwargs):
        """
        Custom update method with rate limiting applied.
        """
        @ratelimit(key='user', rate='5/h', block=True)
        def perform_update(serializer):
            profile = serializer.save(user=self.request.user)
            send_profile_update_notification.delay(profile.user.id)
            logger.info(f"Profile updated for user {profile.user.id}, notification task scheduled.")

        return super().update(request, *args, **kwargs)


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
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(request.user, data=request.data, partial=partial)
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
