#!/usr/bin/env python3
"""
Storage monitoring script for Alex Design project.
Run this periodically to check disk space usage.
"""

import os
import shutil
from pathlib import Path

def check_storage():
    """Check storage usage for media files"""
    
    # Get the media directory path
    media_path = Path(__file__).parent / "media"
    
    if media_path.exists():
        # Calculate total size of media directory
        total_size = sum(f.stat().st_size for f in media_path.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        total_size_gb = total_size_mb / 1024
        
        # Get available disk space
        total, used, free = shutil.disk_usage(media_path)
        free_gb = free / (1024 * 1024 * 1024)
        
        # Count files
        total_files = sum(1 for f in media_path.rglob('*') if f.is_file())
        
        print(f"📊 STORAGE REPORT")
        print(f"=" * 50)
        print(f"Media files: {total_files} files")
        print(f"Media size: {total_size_mb:.1f} MB ({total_size_gb:.2f} GB)")
        print(f"Free space: {free_gb:.1f} GB")
        print(f"=" * 50)
        
        # Warnings
        if free_gb < 1:
            print("⚠️  WARNING: Less than 1GB free space!")
        elif free_gb < 5:
            print("⚠️  WARNING: Less than 5GB free space!")
        else:
            print("✅ Storage looks good!")
            
    else:
        print("❌ Media directory not found!")

if __name__ == "__main__":
    check_storage()
