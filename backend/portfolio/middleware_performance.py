"""
Performance monitoring middleware for Django
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request performance and log slow queries
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests (over 2 seconds)
            if duration > 2.0:
                logger.warning(
                    f"Slow request: {request.method} {request.get_full_path()} "
                    f"took {duration:.2f}s"
                )
            
            # Add performance header for debugging
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # Track API endpoint performance
            if request.path.startswith('/api/'):
                cache_key = f"api_performance:{request.path}:{request.method}"
                # Store last 10 response times for averaging
                times = cache.get(cache_key, [])
                times.append(duration)
                if len(times) > 10:
                    times = times[-10:]
                cache.set(cache_key, times, 3600)  # 1 hour cache
                
        return response
