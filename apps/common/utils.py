from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from django_ratelimit.exceptions import Ratelimited

def custom_exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Try again later."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    return exception_handler(exc, context)
