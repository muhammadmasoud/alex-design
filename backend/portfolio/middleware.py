"""
Custom middleware for handling image serving, optimization, and caching
"""
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.cache import patch_cache_control
from django.core.files.storage import default_storage
import os
import mimetypes
import re
from PIL import Image
import io


class ImageOptimizationMiddleware:
    """
    Middleware to serve optimized images on-the-fly and add proper caching headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an image request that might need optimization
        if self._is_optimizable_image_request(request):
            return self._handle_optimized_image(request)
        
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
    
    def _is_optimizable_image_request(self, request):
        """Check if this is a request for an optimized image variant"""
        return (self._is_image_request(request) and 
                ('_q' in request.path or 
                 request.META.get('HTTP_ACCEPT', '').find('image/webp') != -1))
    
    def _handle_optimized_image(self, request):
        """Handle requests for optimized image variants"""
        try:
            # Extract quality parameter from URL
            quality_match = re.search(r'_q(\d+)', request.path)
            quality = int(quality_match.group(1)) if quality_match else 95
            
            # Get original image path
            original_path = re.sub(r'_q\d+', '', request.path)
            original_path = original_path.replace('/media/', '')
            
            # Check if WebP is requested
            wants_webp = request.META.get('HTTP_ACCEPT', '').find('image/webp') != -1
            
            # Try to serve optimized version
            optimized_response = self._serve_optimized_image(
                original_path, quality, wants_webp
            )
            
            if optimized_response:
                self._add_image_cache_headers(optimized_response)
                return optimized_response
                
        except Exception as e:
            # Log error and fall back to normal processing
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Image optimization error: {e}")
        
        # Fall back to normal processing
        return self.get_response(request)
    
    def _serve_optimized_image(self, image_path, quality, wants_webp):
        """Serve an optimized version of the image"""
        try:
            # Check if original image exists
            if not default_storage.exists(image_path):
                return None
            
            # Open the original image
            with default_storage.open(image_path, 'rb') as image_file:
                with Image.open(image_file) as img:
                    # Determine output format
                    output_format = 'WEBP' if wants_webp else img.format
                    if not output_format:
                        output_format = 'JPEG'
                    
                    # Optimize the image
                    output = io.BytesIO()
                    
                    # Convert RGBA to RGB for JPEG/WebP if needed
                    if output_format in ['JPEG', 'WEBP'] and img.mode in ('RGBA', 'LA', 'P'):
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    
                    # Save with optimization
                    save_kwargs = {'format': output_format, 'optimize': True}
                    
                    if output_format == 'WEBP':
                        save_kwargs.update({
                            'quality': quality,
                            'method': 6,
                            'lossless': quality >= 95
                        })
                    elif output_format == 'JPEG':
                        save_kwargs.update({
                            'quality': quality,
                            'progressive': True,
                            'subsampling': 0
                        })
                    
                    img.save(output, **save_kwargs)
                    output.seek(0)
                    
                    # Create response
                    content_type = f'image/{output_format.lower()}'
                    if output_format == 'JPEG':
                        content_type = 'image/jpeg'
                    
                    response = HttpResponse(output.getvalue(), content_type=content_type)
                    response['Content-Length'] = len(output.getvalue())
                    
                    return response
                    
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error serving optimized image {image_path}: {e}")
            return None
    
    def _add_image_cache_headers(self, response):
        """Add appropriate cache headers to image responses"""
        # Set cache headers for images
        patch_cache_control(response, max_age=86400 * 30)  # 30 days
        response['Vary'] = 'Accept-Encoding, Accept'
        
        # Add CORS headers for cross-origin image access
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        # Add performance headers
        response['X-Content-Type-Options'] = 'nosniff'


class ImageCacheMiddleware:
    """
    Legacy middleware for basic image caching (kept for compatibility)
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
                
                # Try to serve a placeholder image if available
                placeholder_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'placeholder.svg')
                if os.path.exists(placeholder_path):
                    try:
                        with open(placeholder_path, 'rb') as f:
                            response = HttpResponse(f.read(), content_type='image/svg+xml')
                            response.status_code = 200  # Return 200 for placeholder
                            return response
                    except:
                        pass
                
                # Return a 404 response with appropriate content type
                response = HttpResponse(status=404)
                response['Content-Type'] = 'application/json'
                return response
            
            # Re-raise for non-image 404s
            raise
