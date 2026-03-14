import logging
import pytz
from django.utils import translation, timezone
from django.conf import settings

logger = logging.getLogger('apps.core')

SUPPORTED_LANGUAGES = ['en', 'ru', 'kk']
DEFAULT_LANGUAGE = 'en'

class LanguageAndTimezoneMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = self._resolve_language(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        if request.user.is_authenticated and request.user.timezone:
            try:
                tz = pytz.timezone(request.user.timezone)
                timezone.activate(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                timezone.activate(pytz.utc)
        else:
            timezone.activate(pytz.utc)

        response = self.get_response(request)
        translation.deactivate()
        return response
    
    def _resolve_language(self, request):

        if request.user.is_authenticated:
            user_lang = getattr(request.user, 'language', None)
            if user_lang in SUPPORTED_LANGUAGES:
                return user_lang
            
        lang_param = request.GET.get('lang')
        if lang_param in SUPPORTED_LANGUAGES:
            return lang_param
        
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for lang in SUPPORTED_LANGUAGES:
            if accept.startswith(lang):
                return lang
            
        return DEFAULT_LANGUAGE

        