from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from authentication.models import UserModel
from authentication.utils import get_country_from_phone


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = UserModel
        fields = ['phone_number', 'password', 'password_confirm', 'country']
        extra_kwargs = {
            'country': {'required': False}
        }

    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if UserModel.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def validate(self, attrs):
        """Validate password confirmation and auto-detect country"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match.")

        # Auto-detect country from phone number
        phone_number = attrs.get('phone_number')
        if phone_number and not attrs.get('country'):
            country = get_country_from_phone(phone_number)
            if country:
                attrs['country'] = country

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        return UserModel.objects.create_user(**validated_data)


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

        # Authenticate user
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
    """Serializer for user profile information"""
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


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError("New passwords do not match.")

        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
