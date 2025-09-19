#!/bin/bash

# Deployment script for upload fixes
# This script applies the necessary configuration changes to fix 413 errors

set -e

echo "🚀 Applying upload size fixes for Alex Design Portfolio"
echo "==============================================="

# Check if we're running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running with root privileges"
elif command -v sudo >/dev/null 2>&1; then
    echo "✅ Using sudo for privileged operations"
    SUDO="sudo"
else
    echo "❌ Need root privileges or sudo to apply configuration changes"
    exit 1
fi

# Backup current configurations
echo "📦 Creating configuration backups..."
$SUDO cp /etc/nginx/sites-available/alex-design /etc/nginx/sites-available/alex-design.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "⚠️  Nginx config not found, continuing..."

# Copy updated nginx configuration
echo "📝 Updating nginx configuration..."
if [ -f "/home/ubuntu/alex-design/nginx.conf" ]; then
    $SUDO cp /home/ubuntu/alex-design/nginx.conf /etc/nginx/sites-available/alex-design
    echo "✅ Nginx configuration updated"
else
    echo "❌ nginx.conf not found in project directory"
    exit 1
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
$SUDO nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration test failed"
    echo "💡 Restoring backup configuration..."
    $SUDO cp /etc/nginx/sites-available/alex-design.backup.* /etc/nginx/sites-available/alex-design 2>/dev/null || echo "No backup to restore"
    exit 1
fi

# Restart services
echo "🔄 Restarting services..."

# Restart gunicorn
echo "🔄 Restarting gunicorn..."
$SUDO systemctl restart alex-design
if [ $? -eq 0 ]; then
    echo "✅ Gunicorn restarted successfully"
else
    echo "⚠️  Gunicorn restart failed, checking status..."
    $SUDO systemctl status alex-design --no-pager -l
fi

# Reload nginx
echo "🔄 Reloading nginx..."
$SUDO systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx reload failed"
    $SUDO systemctl status nginx --no-pager -l
    exit 1
fi

# Check service status
echo "🔍 Checking service status..."
echo "Gunicorn status:"
$SUDO systemctl is-active alex-design
echo "Nginx status:"
$SUDO systemctl is-active nginx

echo ""
echo "🎉 Upload fixes applied successfully!"
echo ""
echo "📊 New Upload Limits:"
echo "   • Maximum file size: 50MB (increased from 25MB)"
echo "   • Maximum total upload: 1GB (increased from 200MB)"
echo "   • Upload timeout: 10 minutes (increased from 5 minutes)"
echo ""
echo "🔧 Changes applied:"
echo "   • Nginx: client_max_body_size increased to 1GB"
echo "   • Django: DATA_UPLOAD_MAX_MEMORY_SIZE increased to 1GB"
echo "   • Gunicorn: timeout increased to 10 minutes"
echo "   • Frontend: added client-side validation and warnings"
echo ""
echo "✨ Your client should now be able to upload large project albums without 413 errors!"
echo ""
echo "📝 Note: Large uploads (>500MB) will show a confirmation dialog to warn users about upload time."
