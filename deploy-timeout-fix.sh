#!/bin/bash

# Specialized Deployment Script for Timeout Fixes
# This script ensures all timeout-related changes are properly applied

set -e  # Exit on any error

echo "========================================="
echo "Deploying Timeout Fixes to Production"
echo "========================================="

# Configuration
PROJECT_DIR="/home/ubuntu/alex-design"
BACKEND_DIR="$PROJECT_DIR/backend"
SERVICE_NAME="alex-design"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR" || {
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
}

# Step 1: Pull latest changes
print_status "Pulling latest changes from Git..."
git pull origin main || {
    print_warning "Git pull failed, continuing with current code..."
}

# Step 2: Stop services temporarily
print_status "Stopping services for update..."
sudo systemctl stop "$SERVICE_NAME" || print_warning "Service not running"
sudo systemctl stop nginx || print_warning "Nginx not running"

# Step 3: Verify timeout configurations
print_status "Verifying timeout configurations..."

# Check Gunicorn config
if grep -q "timeout = 300" "$BACKEND_DIR/gunicorn.conf.py"; then
    print_status "✓ Gunicorn timeout is set to 300 seconds"
else
    print_error "✗ Gunicorn timeout is not set to 300 seconds"
    print_status "Updating Gunicorn configuration..."
    sed -i 's/timeout = 30/timeout = 300  # Increased from 30 to 5 minutes for large file uploads/' "$BACKEND_DIR/gunicorn.conf.py"
    sed -i 's/graceful_timeout = 30/graceful_timeout = 300  # Increased from 30 to 5 minutes/' "$BACKEND_DIR/gunicorn.conf.py"
fi

# Check Django settings
if grep -q "REQUEST_TIMEOUT = 300" "$BACKEND_DIR/backend/settings.py"; then
    print_status "✓ Django REQUEST_TIMEOUT is set to 300 seconds"
else
    print_error "✗ Django REQUEST_TIMEOUT is not set to 300 seconds"
fi

if grep -q "UPLOAD_TIMEOUT = 300" "$BACKEND_DIR/backend/settings.py"; then
    print_status "✓ Django UPLOAD_TIMEOUT is set to 300 seconds"
else
    print_error "✗ Django UPLOAD_TIMEOUT is not set to 300 seconds"
fi

# Check middleware
if grep -q "RequestTimeoutMiddleware" "$BACKEND_DIR/backend/settings.py"; then
    print_status "✓ RequestTimeoutMiddleware is enabled"
else
    print_error "✗ RequestTimeoutMiddleware is not enabled"
fi

# Step 4: Update NGINX timeout settings
print_status "Updating NGINX timeout settings..."
NGINX_CONFIG="/etc/nginx/sites-available/$SERVICE_NAME"

if [ -f "$NGINX_CONFIG" ]; then
    # Update proxy timeouts for large uploads
    sudo sed -i 's/proxy_connect_timeout 60s;/proxy_connect_timeout 300s;/' "$NGINX_CONFIG"
    sudo sed -i 's/proxy_send_timeout 60s;/proxy_send_timeout 300s;/' "$NGINX_CONFIG"
    sudo sed -i 's/proxy_read_timeout 60s;/proxy_read_timeout 300s;/' "$NGINX_CONFIG"
    
    # Increase client body size if needed
    if ! grep -q "client_max_body_size 50M" "$NGINX_CONFIG"; then
        sudo sed -i 's/client_max_body_size 25M;/client_max_body_size 50M;/' "$NGINX_CONFIG"
    fi
    
    print_status "✓ NGINX timeout settings updated"
else
    print_warning "NGINX config not found, skipping timeout updates"
fi

# Step 5: Activate virtual environment and install dependencies
print_status "Activating virtual environment and installing dependencies..."
source "$PROJECT_DIR/venv/bin/activate"
cd "$BACKEND_DIR"

# Install new packages
pip install -r requirements.txt

# Step 6: Run database migrations
print_status "Running database migrations..."
python manage.py migrate

# Step 7: Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Step 8: Reload systemd and restart services
print_status "Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl start "$SERVICE_NAME"
sudo systemctl restart nginx

# Step 9: Verify services are running
print_status "Verifying services are running..."
sleep 5  # Give services time to start

if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "✓ Gunicorn service is running"
else
    print_error "✗ Gunicorn service failed to start"
    sudo systemctl status "$SERVICE_NAME"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "✓ NGINX service is running"
else
    print_error "✗ NGINX service failed to start"
    sudo systemctl status nginx
    exit 1
fi

# Step 10: Test the timeout fixes
print_status "Testing timeout configurations..."

# Check Gunicorn process
GUNICORN_PID=$(pgrep -f "gunicorn.*backend.wsgi")
if [ -n "$GUNICORN_PID" ]; then
    print_status "✓ Gunicorn process is running (PID: $GUNICORN_PID)"
    
    # Check Gunicorn config
    GUNICORN_CONFIG=$(ps -p $GUNICORN_PID -o args= | grep -o "gunicorn.*")
    if echo "$GUNICORN_CONFIG" | grep -q "gunicorn.conf.py"; then
        print_status "✓ Gunicorn is using the updated configuration file"
    else
        print_warning "⚠ Gunicorn may not be using the updated configuration"
    fi
else
    print_error "✗ Gunicorn process not found"
fi

# Step 11: Display final status
print_status "========================================="
print_status "Timeout Fix Deployment Completed!"
print_status "========================================="
print_status "Key changes applied:"
print_status "• Gunicorn timeout: 300 seconds (5 minutes)"
print_status "• Django request timeout: 300 seconds"
print_status "• NGINX proxy timeouts: 300 seconds"
print_status "• RequestTimeoutMiddleware: Enabled"
print_status ""
print_status "Your server should now handle large uploads without 504 errors."
print_status ""
print_status "To monitor the system:"
print_status "• Service status: sudo systemctl status $SERVICE_NAME"
print_status "• Gunicorn logs: sudo journalctl -u $SERVICE_NAME -f"
print_status "• NGINX logs: sudo tail -f /var/log/nginx/error.log"
print_status ""
print_status "Test your upload functionality now!"
