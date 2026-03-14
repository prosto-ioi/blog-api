import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegisterSerializer, LanguageSerializer, TimezoneSerializer

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

            _send_welcome_email(user)

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
    
def _send_welcome_email(user) -> None:
    try:
        with translation.override(user.language):
            subject = render_to_string('emails/welcome/subject.txt', {'user': user}).strip()
            body = render_to_string('emails/welcome/body.txt', {'user': user})
        send_mail(subject, body, 'noreply@blogapi.com', [user.email])
        logger.info('Welcome email sent to: %s', user.email)
    except Exception:
        logger.exception('Failed to send welcome email to: %s', user.email)


@extend_schema(tags=['Auth'])
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def set_language(request: Request) -> Response:
    serializer = LanguageSerializer(data=request.data)
    if serializer.is_valid():
        request.user.language = serializer.validated_data['language']
        request.user.save(update_fields=['language'])
        return Response({'detail': _('Language updated successfully.')})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def set_timezone(request: Request)-> Response:
    serializer = TimezoneSerializer(data=request.data)
    if serializer.is_valid():
        request.user.timezone = serializer.validated_data['timezone']
        request.user.save(update_fields=['timezone'])
        return Response({'detail': _('Timezone updated successfully.')})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
