from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from authentication.models import UserModel


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = UserModel
        fields = ['phone_number', 'password', 'country']

    def create(self, validated_data):
        return UserModel.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            country=validated_data.get('country')
        )


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=make_password(password))
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is inactive.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Incorrect phone number or password.")
        else:
            raise serializers.ValidationError("Both phone number and password are required.")
        return data
