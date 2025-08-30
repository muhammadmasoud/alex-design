"""
Custom middleware for handling image serving and caching
"""
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.cache import patch_cache_control
from django.core.files.storage import default_storage
import os
import mimetypes
import signal
import threading
import time


class RequestTimeoutMiddleware:
    """
    Middleware to handle request timeouts for long-running operations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'REQUEST_TIMEOUT', 300)  # Default 5 minutes

    def __call__(self, request):
        # Set a timeout for the request
        if request.path.endswith('/bulk_upload/'):
            # Increase timeout for bulk upload operations
            request_timeout = getattr(settings, 'UPLOAD_TIMEOUT', 300)
        else:
            request_timeout = self.timeout
        
        # Start a timer thread
        timer = threading.Timer(request_timeout, self._timeout_handler, args=[request])
        timer.start()
        
        try:
            response = self.get_response(request)
            timer.cancel()  # Cancel timer if request completes
            return response
        except Exception as e:
            timer.cancel()
            raise e
    
    def _timeout_handler(self, request):
        """Handle request timeout"""
        # This would be called if the request takes too long
        # In practice, Django handles timeouts at the WSGI level
        pass


class ImageServingMiddleware:
    """
    Middleware to serve images with proper caching headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add caching headers for image files
        if self._is_image_request(request):
            self._add_image_cache_headers(response)
        
        return response
    
    def _is_image_request(self, request):
        """Check if the request is for an image file"""
        return (request.path.startswith('/media/') and 
                any(request.path.lower().endswith(ext) 
                    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']))
    
    def _add_image_cache_headers(self, response):
        """Add appropriate caching headers for images"""
        # Cache images for 30 days
        patch_cache_control(response, max_age=86400 * 30, public=True)
        
        # Add CORS headers for images
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Accept, Accept-Encoding, Range'
        
        # Add content type headers if missing
        if 'Content-Type' not in response:
            path = response.get('X-Accel-Redirect', '')
            if path:
                content_type, _ = mimetypes.guess_type(path)
                if content_type:
                    response['Content-Type'] = content_type
