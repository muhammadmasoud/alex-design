#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from portfolio.models import Project

# Get the project
p = Project.objects.get(title='asdas')
print(f"Project: {p.title}")
print(f"Main image: {p.image}")
print(f"Optimized image medium: {p.optimized_image_medium}")
print(f"Optimized image: {p.optimized_image}")
print(f"Original file path: {p.original_file_path}")
print()

print("Album images:")
for img in p.album_images.all()[:3]:
    print(f"  Image {img.id}: optimized_medium={img.optimized_image_medium}, original_path={img.original_file_path}")
