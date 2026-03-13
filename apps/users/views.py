import logging

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegisterSerializer

logger = logging.getLogger('apps.users')


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class UserRegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request) -> Response:
        logger.info('Registration attempt for email: %s', request.data.get('email'))
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info('User registered successfully: %s', user.email)
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        logger.warning('Registration failed for email: %s. Errors: %s',
                       request.data.get('email'), serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)