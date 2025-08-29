#!/bin/bash
# Performance monitoring script

echo "🔍 Performance Monitoring Report - $(date)"
echo "========================================="

# Check Redis status
echo "📊 Redis Status:"
if command -v redis-cli &> /dev/null; then
    redis-cli ping
    echo "Redis memory usage: $(redis-cli info memory | grep used_memory_human | cut -d: -f2)"
else
    echo "Redis CLI not available"
fi

# Check disk space
echo -e "\n💾 Disk Usage:"
df -h /home/ubuntu/alex-design/backend/media/ 2>/dev/null | tail -1 || echo "Media directory not found"

# Check image cache size
echo -e "\n🖼️  Image Cache Statistics:"
cache_dir="/home/ubuntu/alex-design/backend/media/cache"
if [ -d "$cache_dir" ]; then
    echo "Cached images: $(find $cache_dir -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" 2>/dev/null | wc -l)"
    echo "Cache size: $(du -sh $cache_dir 2>/dev/null | cut -f1)"
else
    echo "Cache directory not found"
fi

# Check Nginx error logs for image-related issues
echo -e "\n🚨 Recent Image-Related Errors:"
if [ -f "/var/log/nginx/error.log" ]; then
    sudo tail -20 /var/log/nginx/error.log | grep -i "image\|media" || echo "No recent image errors"
else
    echo "Nginx error log not found"
fi

# Test image loading speed
echo -e "\n⚡ Image Loading Speed Test:"
url="http://localhost/media/"
if command -v curl &> /dev/null; then
    response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url" 2>/dev/null || echo "Test failed")
    echo "Response time: ${response_time}s"
else
    echo "Curl not available for speed test"
fi

echo -e "\n✅ Monitoring complete"
