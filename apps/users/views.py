from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import UserRegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class UserRegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        logger.info('Registration attempt for email: %s', request.data.get('email'))
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info('User registered successfully: %s', user.email)

            return Response({
                "user": serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }

            }, status=status.HTTP_201_CREATED)
        else:
            logger.warning('Registration failed for email: %s. Errors: %s', request.data.get('email'), serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
