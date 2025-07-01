from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserAuthViewSet(ViewSet):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Register",
        operation_description="Register a new user with phone number and password.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(description="User registered successfully"),
            400: openapi.Response(description="Bad Request")
        },
        tags=['Authentication'],
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Login",
        operation_description="Login with phone number and password to receive JWT tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(description="Login successful, returns JWT tokens"),
            400: openapi.Response(description="Invalid credentials")
        },
        tags=['Authentication'],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
