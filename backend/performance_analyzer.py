#!/usr/bin/env python3
"""
Performance Analysis and Monitoring Script for Alex Design Portfolio
"""
import os
import sys
import django
from pathlib import Path
import time
import psutil
import requests
from urllib.parse import urljoin

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.test.utils import override_settings
from django.db import connection
from portfolio.models import Project, Service, ProjectImage, ServiceImage


class PerformanceAnalyzer:
    def __init__(self):
        self.results = {}
    
    def analyze_database_performance(self):
        """Analyze database query performance"""
        print("🗄️  Analyzing database performance...")
        
        start_time = time.time()
        
        # Test common queries
        queries = {
            'Projects count': lambda: Project.objects.count(),
            'Services count': lambda: Service.objects.count(),
            'Project images count': lambda: ProjectImage.objects.count(),
            'Service images count': lambda: ServiceImage.objects.count(),
            'Projects with images': lambda: Project.objects.filter(image__isnull=False).count(),
            'Projects with categories': lambda: Project.objects.prefetch_related('categories').count(),
            'Services with albums': lambda: Service.objects.prefetch_related('album_images').count(),
        }
        
        for query_name, query_func in queries.items():
            start = time.time()
            result = query_func()
            end = time.time()
            duration = (end - start) * 1000  # Convert to milliseconds
            print(f"  {query_name}: {result} ({duration:.2f}ms)")
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        total_time = (time.time() - start_time) * 1000
        print(f"  Total database analysis time: {total_time:.2f}ms")
        
        self.results['database'] = total_time
    
    def analyze_media_files(self):
        """Analyze media file performance"""
        print("\\n📁 Analyzing media files...")
        
        media_path = Path('media')
        if not media_path.exists():
            print("  ❌ Media directory not found!")
            return
        
        total_files = 0
        total_size = 0
        large_files = []
        
        for root, dirs, files in os.walk(media_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_files += 1
                    total_size += file_size
                    
                    # Flag files larger than 1MB
                    if file_size > 1024 * 1024:
                        large_files.append((file_path, file_size / (1024 * 1024)))
                        
                except OSError:
                    pass
        
        print(f"  Total files: {total_files}")
        print(f"  Total size: {total_size / (1024 * 1024):.2f} MB")
        print(f"  Average file size: {(total_size / total_files) / 1024:.1f} KB")
        
        if large_files:
            print(f"  Files > 1MB ({len(large_files)} files):")
            for file_path, size_mb in sorted(large_files, key=lambda x: x[1], reverse=True):
                print(f"    {file_path}: {size_mb:.2f} MB")
        else:
            print("  ✅ No files larger than 1MB found")
        
        self.results['media'] = {
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'large_files': len(large_files)
        }
    
    def analyze_system_resources(self):
        """Analyze system resource usage"""
        print("\\n💻 Analyzing system resources...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"  CPU usage: {cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"  Memory usage: {memory.percent}% ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
        
        # Disk usage
        disk = psutil.disk_usage('.')
        print(f"  Disk usage: {disk.percent}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)")
        
        # Network connections (if any)
        connections = psutil.net_connections()
        active_connections = [c for c in connections if c.status == 'ESTABLISHED']
        print(f"  Active network connections: {len(active_connections)}")
        
        self.results['system'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent
        }
    
    def test_api_endpoints(self, base_url="http://localhost:8000"):
        """Test API endpoint performance"""
        print(f"\\n🌐 Testing API endpoints at {base_url}...")
        
        endpoints = [
            '/api/projects/',
            '/api/services/', 
            '/api/categories/',
            '/api/admin/projects/',
        ]
        
        for endpoint in endpoints:
            try:
                url = urljoin(base_url, endpoint)
                start = time.time()
                response = requests.get(url, timeout=10)
                end = time.time()
                
                duration = (end - start) * 1000
                status = "✅" if response.status_code == 200 else "❌"
                
                print(f"  {endpoint}: {status} {response.status_code} ({duration:.0f}ms)")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'results' in data:
                            print(f"    Results: {len(data['results'])} items")
                        elif isinstance(data, list):
                            print(f"    Results: {len(data)} items")
                    except:
                        pass
                        
            except requests.exceptions.RequestException as e:
                print(f"  {endpoint}: ❌ Connection failed ({str(e)})")
    
    def generate_optimization_recommendations(self):
        """Generate optimization recommendations based on analysis"""
        print("\\n📋 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Database recommendations
        if self.results.get('database', 0) > 100:
            recommendations.append("🗄️  Consider adding database indexes for frequently queried fields")
            recommendations.append("🗄️  Use select_related() and prefetch_related() for related queries")
        
        # Media file recommendations
        media_results = self.results.get('media', {})
        if media_results.get('large_files', 0) > 0:
            recommendations.append(f"📁 Found {media_results['large_files']} files > 1MB - consider further optimization")
        
        if media_results.get('total_size_mb', 0) > 50:
            recommendations.append("📁 Total media size is large - consider implementing a CDN")
        
        # System recommendations
        system_results = self.results.get('system', {})
        if system_results.get('cpu_percent', 0) > 80:
            recommendations.append("💻 High CPU usage detected - consider optimizing code or upgrading hardware")
        
        if system_results.get('memory_percent', 0) > 80:
            recommendations.append("💻 High memory usage detected - consider optimizing queries or upgrading RAM")
        
        # General recommendations
        recommendations.extend([
            "🚀 Enable gzip compression in your web server",
            "🚀 Implement browser caching for static files",
            "🚀 Use a reverse proxy like Nginx for better performance", 
            "🚀 Consider implementing lazy loading for images",
            "🚀 Use WebP format for better image compression",
            "🚀 Implement image responsive sizing",
            "🚀 Monitor performance with tools like Google PageSpeed Insights"
        ])
        
        for i, recommendation in enumerate(recommendations, 1):
            print(f"{i:2d}. {recommendation}")
    
    def run_analysis(self):
        """Run complete performance analysis"""
        print("🔍 ALEX DESIGN PORTFOLIO - PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        self.analyze_database_performance()
        self.analyze_media_files()
        self.analyze_system_resources()
        
        # Only test API if Django development server might be running
        try:
            self.test_api_endpoints()
        except Exception:
            print("\\n🌐 API endpoint testing skipped (server not running)")
        
        self.generate_optimization_recommendations()
        
        print("\\n✅ Performance analysis complete!")


def main():
    """Main function"""
    analyzer = PerformanceAnalyzer()
    analyzer.run_analysis()


if __name__ == '__main__':
    main()
