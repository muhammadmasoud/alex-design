"""
Custom utilities for the portfolio app
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler to catch serialization errors and other issues
    """
    # Call the default exception handler first
    response = exception_handler(exc, context)
    
    if response is None:
        # If DRF didn't handle it, log it and return a proper error
        logger.error(f"Unhandled exception: {exc}")
        logger.error(f"Exception type: {type(exc)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return a proper error response instead of 500
        return Response({
            'error': 'An unexpected error occurred',
            'detail': str(exc) if hasattr(exc, '__str__') else 'Unknown error',
            'type': str(type(exc).__name__)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Log the error for debugging
    logger.error(f"DRF handled exception: {exc}")
    logger.error(f"Response status: {response.status_code}")
    
    return response
