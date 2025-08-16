#!/bin/bash

echo "🚀 Deploying Upload Performance Optimizations..."

# Create nginx temp directory
echo "📁 Creating nginx temp directory..."
sudo mkdir -p /tmp/nginx_client_temp
sudo chown -R www-data:www-data /tmp/nginx_client_temp
sudo chmod 755 /tmp/nginx_client_temp

# Copy optimized nginx configuration
echo "🔧 Updating nginx configuration..."
sudo cp nginx.conf /etc/nginx/sites-available/alex-design
sudo ln -sf /etc/nginx/sites-available/alex-design /etc/nginx/sites-enabled/alex-design

# Test nginx configuration
echo "✅ Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Restart nginx
    echo "🔄 Restarting nginx..."
    sudo systemctl restart nginx
    
    # Navigate to backend
    cd backend
    
    # Apply Django migrations (if any)
    echo "📊 Checking for migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    # Collect static files
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Restart gunicorn with optimized configuration
    echo "🔄 Restarting gunicorn with optimizations..."
    sudo systemctl restart gunicorn
    
    # Build and deploy frontend
    echo "🎨 Building and deploying frontend..."
    cd ../frontend
    npm run build
    sudo cp -r dist/* /var/www/alex-design/
    sudo chown -R www-data:www-data /var/www/alex-design/
    sudo chmod -R 755 /var/www/alex-design/
    
    echo "✅ All optimizations deployed successfully!"
    echo ""
    echo "🚀 Upload Performance Improvements:"
    echo "   • Django streaming uploads (disk-based for large files)"
    echo "   • Nginx direct upload streaming"
    echo "   • Gunicorn memory optimization"
    echo "   • Better temporary file handling"
    echo ""
    echo "💡 Expected improvements:"
    echo "   • Faster upload speeds (reduced memory overhead)"
    echo "   • Better handling of concurrent uploads"
    echo "   • Reduced server memory usage"
    echo "   • More stable large file transfers"
    
else
    echo "❌ Nginx configuration test failed. Please check the configuration."
    exit 1
fi

echo ""
echo "🔍 Checking services status..."
sudo systemctl status nginx --no-pager -l
sudo systemctl status gunicorn --no-pager -l

echo ""
echo "🎯 Ready for testing! Try uploading large files now."
