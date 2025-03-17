from django.contrib.messages.middleware import MessageMiddleware
from django.utils.deprecation import MiddlewareMixin

class ClearMessageMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Clear messages after they are displayed
        if hasattr(request, '_messages'):
            list(request._messages)
        return response
