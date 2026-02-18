import logging
import time

logger = logging.getLogger('django.request')

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        logger.debug(
            'Request: %s %s, Status: %d, Duration: %.2fs, User: %s',
            request.method,
            request.path,
            response.status_code,
            duration,
            request.user if request.user.is_authenticated else 'Anonymous'
        )
        return response
    