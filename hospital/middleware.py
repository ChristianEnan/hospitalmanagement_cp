from django.shortcuts import redirect
from django.urls import reverse

class AccessDeniedMiddleware:
    """
    Middleware to redirect 403 errors to custom access denied page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # If 403 Forbidden, redirect to access denied page
        if response.status_code == 403:
            return redirect('access-denied')
        
        return response
