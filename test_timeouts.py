#!/usr/bin/env python3
"""
Test script to verify timeout configurations
Run this script to check if all timeout settings are properly configured
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def test_timeout_configurations():
    """Test all timeout configurations"""
    print("🔍 Testing Timeout Configurations")
    print("=" * 50)
    
    # Test Django settings
    print("\n📋 Django Settings:")
    print(f"  REQUEST_TIMEOUT: {getattr(settings, 'REQUEST_TIMEOUT', 'NOT SET')} seconds")
    print(f"  UPLOAD_TIMEOUT: {getattr(settings, 'UPLOAD_TIMEOUT', 'NOT SET')} seconds")
    print(f"  IMAGE_OPTIMIZATION_TIMEOUT: {getattr(settings, 'IMAGE_OPTIMIZATION_TIMEOUT', 'NOT SET')} seconds")
    
    # Test file upload settings
    print(f"\n📁 File Upload Settings:")
    print(f"  FILE_UPLOAD_MAX_MEMORY_SIZE: {getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 'NOT SET')} bytes")
    print(f"  DATA_UPLOAD_MAX_MEMORY_SIZE: {getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 'NOT SET')} bytes")
    print(f"  MAX_IMAGE_SIZE: {getattr(settings, 'MAX_IMAGE_SIZE', 'NOT SET')} bytes")
    
    # Test database settings
    print(f"\n🗄️  Database Settings:")
    db_options = settings.DATABASES['default'].get('OPTIONS', {})
    print(f"  connect_timeout: {db_options.get('connect_timeout', 'NOT SET')} seconds")
    print(f"  statement_timeout: {db_options.get('options', 'NOT SET')}")
    
    # Test production vs development
    print(f"\n🌍 Environment:")
    print(f"  IS_PRODUCTION: {getattr(settings, 'IS_PRODUCTION', 'NOT SET')}")
    print(f"  DEBUG: {getattr(settings, 'DEBUG', 'NOT SET')}")
    
    # Validate timeout values
    print(f"\n✅ Validation:")
    issues = []
    
    if getattr(settings, 'REQUEST_TIMEOUT', 0) < 3600:
        issues.append("REQUEST_TIMEOUT should be at least 3600 seconds (1 hour)")
    
    if getattr(settings, 'UPLOAD_TIMEOUT', 0) < 3600:
        issues.append("UPLOAD_TIMEOUT should be at least 3600 seconds (1 hour)")
    
    if getattr(settings, 'IMAGE_OPTIMIZATION_TIMEOUT', 0) < 1800:
        issues.append("IMAGE_OPTIMIZATION_TIMEOUT should be at least 1800 seconds (30 minutes)")
    
    if not db_options.get('connect_timeout'):
        issues.append("Database connect_timeout should be set")
    
    if not db_options.get('options') or 'statement_timeout' not in str(db_options.get('options', '')):
        issues.append("Database statement_timeout should be set")
    
    if issues:
        print("  ❌ Issues found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✅ All timeout configurations look good!")
    
    print(f"\n📊 Summary:")
    print(f"  Request timeout: {getattr(settings, 'REQUEST_TIMEOUT', 0)}s")
    print(f"  Upload timeout: {getattr(settings, 'UPLOAD_TIMEOUT', 0)}s") 
    print(f"  Image optimization timeout: {getattr(settings, 'IMAGE_OPTIMIZATION_TIMEOUT', 0)}s")
    print(f"  Database connect timeout: {db_options.get('connect_timeout', 'Not set')}s")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_timeout_configurations()
    sys.exit(0 if success else 1)
