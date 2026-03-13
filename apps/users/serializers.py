from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']  # было пусто!

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords didn't match"})
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)