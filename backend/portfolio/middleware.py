"""
Custom middleware for handling image serving and caching
"""
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.cache import patch_cache_control
import os
import mimetypes


class ImageCacheMiddleware:
    """
    Middleware to add proper caching headers to image responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add caching headers for image files
        if (request.path.startswith('/media/') and 
            any(request.path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'])):
            
            # Set cache headers for images
            patch_cache_control(response, max_age=86400 * 30)  # 30 days
            response['Vary'] = 'Accept-Encoding'
            
            # Add CORS headers for cross-origin image access
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response


class ImageErrorHandlerMiddleware:
    """
    Middleware to handle missing image files gracefully
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Http404:
            # If it's a media file request that failed, check if it's an image
            if (request.path.startswith('/media/') and 
                any(request.path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'])):
                
                # Log the missing image
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Missing image file requested: {request.path}")
                
                # Return a 404 response instead of raising an exception
                response = HttpResponse(status=404)
                response['Content-Type'] = 'application/json'
                return response
            
            # Re-raise for non-image 404s
            raise
