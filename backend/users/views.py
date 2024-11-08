# backend/users/views.py

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
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from users.utils import send_2fa_code  # Utility function to send SMS via Twilio
from rest_framework.throttling import AnonRateThrottle

# Initialize logger once at the top
logger = logging.getLogger('users')


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  # Using 'pk' instead of 'id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """
        Limit queryset to the profile of the logged-in user.
        """
        return self.queryset.filter(user=self.request.user)

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
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """
        Limit queryset to the logged-in user.
        """
        return self.queryset.filter(pk=self.request.user.pk)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_2fa(self, request):
        """
        Allows the user to enable or disable 2FA.
        """
        user = request.user
        enable_2fa = request.data.get('enable_2fa')

        if enable_2fa is None:
            return Response({'detail': 'Please provide a value for enable_2fa.'}, status=status.HTTP_400_BAD_REQUEST)

        enable_2fa = str(enable_2fa).lower() in ['true', '1', 'yes']

        user.is_2fa_enabled = enable_2fa
        user.save(update_fields=['is_2fa_enabled'])

        if enable_2fa:
            # Ensure the user has a phone number
            if not user.profile.phone:
                return Response({'detail': 'Phone number is required to enable 2FA.'}, status=status.HTTP_400_BAD_REQUEST)
            # Generate and send the 2FA code to the user's phone
            user.generate_two_factor_code()
            send_2fa_code(user.profile.phone, user.two_factor_code)
            logger.info(f"2FA enabled and code sent for user {user.id}")
            return Response({'detail': '2FA enabled. Verification code sent to your phone.'}, status=status.HTTP_200_OK)
        else:
            # Clear any existing 2FA code
            user.clear_two_factor_code()
            logger.info(f"2FA disabled for user {user.id}")
            return Response({'detail': '2FA disabled.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_2fa_code(self, request):
        """
        Verifies the 2FA code when enabling 2FA.
        """
        user = request.user
        code = request.data.get('code')

        if not code:
            return Response({'detail': 'Verification code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.verify_two_factor_code(code):
            logger.info(f"2FA setup completed for user {user.id}")
            return Response({'detail': '2FA is now fully enabled.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid or expired verification code.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserSignupView(CreateAPIView):
    """
    API view for signing up new users.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    throttle_classes = [AnonRateThrottle]  # Apply throttling if necessary

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


class CustomLoginView(APIView):
    """
    Custom login view to handle 2FA if enabled.
    """
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [AnonRateThrottle]  # Apply throttling if necessary

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        code = request.data.get('code')

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            if not user.check_password(password):
                raise AuthenticationFailed('Invalid credentials')

            if not user.is_active:
                raise AuthenticationFailed('Account is disabled.')

            if user.is_2fa_enabled:
                if code:
                    if not user.verify_two_factor_code(code):
                        raise AuthenticationFailed('Invalid or expired 2FA code')
                else:
                    # Generate and send a new 2FA code
                    user.generate_two_factor_code()
                    send_2fa_code(user.profile.phone, user.two_factor_code)
                    return Response({'detail': '2FA code sent to your phone.'}, status=status.HTTP_200_OK)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials')
