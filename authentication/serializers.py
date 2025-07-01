from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from authentication.models import UserModel
from authentication.utils import validate_password_uppercase


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password, validate_password_uppercase],
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters with at least one uppercase letter"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Must match the password field"
    )

    class Meta:
        model = UserModel
        fields = ['phone_number', 'password', 'password_confirm', 'country']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = UserModel.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            country=validated_data.get('country')
        )
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError("Both phone number and password are required.")

        user = authenticate(
            request=self.context.get('request'),
            username=phone_number,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'id', 'phone_number', 'country', 'is_verified',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'phone_number', 'is_verified',
            'date_joined', 'created_at', 'updated_at'
        ]
