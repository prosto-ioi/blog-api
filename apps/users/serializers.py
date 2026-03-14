import pytz
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User, LANGUAGE_CHOICES

SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]


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
    
class LanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=SUPPORTED_LANGUAGES)


class TimezoneSerializer(serializers.Serializer):
    timezone = serializers.CharField()

    def validate_timezone(self, value: str) -> str:
        if value not in pytz.all_timezones:
            raise serializers.ValidationError(
                _('Invalid timezone. Please use a valid IANA timezone identifier.')

            )
        return value
            