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
    Middleware to handle request timeouts for long-running operations and track timing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'REQUEST_TIMEOUT', 3600)  # Default 1 hour

    def __call__(self, request):
        import time
        start_time = time.time()
        
        # Set a timeout for the request
        if request.path.endswith('/bulk_upload/'):
            # Increase timeout for bulk upload operations
            request_timeout = getattr(settings, 'UPLOAD_TIMEOUT', 3600)
        else:
            request_timeout = self.timeout
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add timing and timeout headers to response for debugging
        response['X-Request-Timeout'] = str(request_timeout)
        response['X-Processing-Time'] = f"{processing_time:.3f}s"
        
        # Log slow requests for debugging
        if processing_time > 5.0:  # Log requests taking more than 5 seconds
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Slow request: {request.method} {request.path} took {processing_time:.2f}s")
        
        return response
    
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
        """Add appropriate caching headers for images with aggressive optimization"""
        # Cache images for 1 year (they're immutable with unique names)
        patch_cache_control(response, max_age=31536000, public=True, immutable=True)
        
        # Add CORS headers for images
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Accept, Accept-Encoding, Range'
        
        # Enable HTTP/2 Server Push hints for browsers
        response['Link'] = '<{}>; rel=preload; as=image'.format(response.get('X-Original-URL', ''))
        
        # Add content type headers if missing
        if 'Content-Type' not in response:
            path = response.get('X-Accel-Redirect', '')
            if path:
                content_type, _ = mimetypes.guess_type(path)
                if content_type:
                    response['Content-Type'] = content_type
        
        # Add performance headers for faster loading
        response['X-Content-Type-Options'] = 'nosniff'
        response['Accept-Ranges'] = 'bytes'  # Enable range requests for large images
