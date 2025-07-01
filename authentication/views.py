from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import logout

from authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


class UserAuthViewSet(ViewSet):
    """ViewSet for user authentication operations"""

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['register', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Register User",
        operation_description="Register a new user with phone number and password.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "message": "User registered successfully",
                        "user_id": 1
                    }
                }
            ),
            400: openapi.Response(description="Bad Request")
        },
        tags=['Authentication'],
    )
    def register(self, request):
        """Register a new user"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user_id": user.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Login User",
        operation_description="Login with phone number and password to receive JWT tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful, returns JWT tokens",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "id": 1,
                            "phone_number": "+998901234567",
                            "country": "Uzbekistan"
                        }
                    }
                }
            ),
            400: openapi.Response(description="Invalid credentials")
        },
        tags=['Authentication'],
    )
    def login(self, request):
        """Login user and return JWT tokens"""
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            # Update last login
            user.save(update_fields=['last_login'])

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Logout User",
        operation_description="Logout user and blacklist refresh token.",
        responses={
            200: openapi.Response(description="Logout successful"),
            400: openapi.Response(description="Bad Request")
        },
        tags=['Authentication'],
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user"""
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            logout(request)
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Get User Profile",
        operation_description="Get current user profile information.",
        responses={
            200: UserProfileSerializer,
            401: openapi.Response(description="Unauthorized")
        },
        tags=['User Profile'],
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update User Profile",
        operation_description="Update user profile information.",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized")
        },
        tags=['User Profile'],
    )
    @profile.mapping.put
    def update_profile(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Change Password",
        operation_description="Change user password.",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="Password changed successfully"),
            400: openapi.Response(description="Bad Request"),
            401: openapi.Response(description="Unauthorized")
        },
        tags=['User Profile'],
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
