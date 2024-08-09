import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileSerializer


# Get an instance of a logger
logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)


@extend_schema_view(
    post=extend_schema(
        description="User Signup Endpoint",
        request=CustomUserSerializer,
        responses={201: CustomUserSerializer},
    )
)
class CustomUserSignupView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Log the incoming request data for debugging
        logger.debug(f"Received signup request data: {request.data}")

        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Log success
            logger.debug(f"User created successfully: {user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Log the errors for debugging
            logger.error(f"Signup failed due to validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserProfileViewSet(viewsets.ModelViewSet):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         return UserProfile.objects.filter(user=self.request.user)
