from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from authentication.models import COUNTRY_CHOICES
from authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
)
from rest_framework_simplejwt.exceptions import TokenError


class RegisterViewSet(ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # Support form data

    @swagger_auto_schema(
        operation_summary="Register User",
        operation_description="Register a new user with phone number, password, and country using form data. The country field is a dropdown based on predefined choices.",
        manual_parameters=[
            openapi.Parameter(
                name='phone_number',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="User's phone number (e.g., +998901234567)",
                max_length=30,
                example="+998901234567"
            ),
            openapi.Parameter(
                name='password',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Password (minimum 8 characters, must include at least one uppercase letter)",
                min_length=8,
                format='password'
            ),
            openapi.Parameter(
                name='password_confirm',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Must match the password field",
                format='password'
            ),
            openapi.Parameter(
                name='country',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="User's country (select from dropdown)",
                enum=[choice[0] for choice in COUNTRY_CHOICES],
                default="Uzbekistan",
                example="Uzbekistan"
            ),
        ],
        consumes=['multipart/form-data', 'application/x-www-form-urlencoded'],
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="User registered successfully"),
                        'user_info': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, example="+998901234567"),
                                'country': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=[choice[0] for choice in COUNTRY_CHOICES],
                                    example="Uzbekistan"
                                ),
                            }
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "message": "User registered successfully",
                        "user_info": {
                            "phone_number": "+998901234567",
                            "country": "Uzbekistan"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "phone_number": ["This field is required."],
                        "password": ["Password must be at least 8 characters."],
                        "password_confirm": ["Passwords do not match."],
                        "country": ["Invalid choice."]
                    }
                }
            )
        },
        tags=['Authentication'],
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user_info": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # Support form data

    @swagger_auto_schema(
        operation_summary="Login User",
        operation_description="Authenticate a user with phone number and password using form data. Returns access and refresh tokens along with user details.",
        manual_parameters=[
            openapi.Parameter(
                name='phone_number',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="User's phone number (e.g., +998901234567)",
                max_length=30,
                example="+998901234567"
            ),
            openapi.Parameter(
                name='password',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="User's password",
                format='password'
            ),
        ],
        consumes=['multipart/form-data', 'application/x-www-form-urlencoded'],
        responses={
            200: openapi.Response(
                description="User logged in successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token",
                                                 example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token",
                                                  example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, example="+998901234567"),
                                'country': openapi.Schema(type=openapi.TYPE_STRING, example="UZ"),
                            }
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "phone_number": "+998901234567",
                            "country": "UZ"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "phone_number": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            )
        },
        tags=['Authentication'],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            user.save(update_fields=['last_login'])

            return Response(
                {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserProfileSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Logout User",
        operation_description="Log out an authenticated user by blacklisting the provided refresh token using form data. Requires a valid JWT access token in the Authorization header (Bearer <access_token>).",
        manual_parameters=[
            openapi.Parameter(
                name='refresh',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="The refresh token to blacklist for logout",
                example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            ),
        ],
        security=[{'Bearer': []}],
        consumes=['multipart/form-data', 'application/x-www-form-urlencoded'],
        responses={
            200: openapi.Response(
                description="User logged out successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="User logged out successfully")
                    }
                ),
                examples={
                    "application/json": {
                        "message": "User logged out successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "refresh": ["This field is required."],
                        "detail": ["Invalid token."]
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized - Authentication credentials were not provided or are invalid",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        },
        tags=['Authentication'],
    )
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {"refresh": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "User logged out successfully"},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": ["Invalid token."]},
                status=status.HTTP_400_BAD_REQUEST
            )