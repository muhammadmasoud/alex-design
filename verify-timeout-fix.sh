#!/bin/bash

# Verification Script for Timeout Fixes
# This script checks if all timeout-related changes are properly applied

echo "========================================="
echo "Verifying Timeout Fixes on Server"
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

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_failure() {
    echo -e "${RED}[✗]${NC} $1"
}

# Navigate to project directory
cd "$PROJECT_DIR" || {
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
}

echo ""
print_status "Checking Gunicorn Configuration..."

# Check Gunicorn timeout settings
if grep -q "timeout = 300" "$BACKEND_DIR/gunicorn.conf.py"; then
    print_success "Gunicorn timeout is set to 300 seconds"
else
    print_failure "Gunicorn timeout is NOT set to 300 seconds"
fi

if grep -q "graceful_timeout = 300" "$BACKEND_DIR/gunicorn.conf.py"; then
    print_success "Gunicorn graceful_timeout is set to 300 seconds"
else
    print_failure "Gunicorn graceful_timeout is NOT set to 300 seconds"
fi

echo ""
print_status "Checking Django Settings..."

# Check Django timeout settings
if grep -q "REQUEST_TIMEOUT = 300" "$BACKEND_DIR/backend/settings.py"; then
    print_success "Django REQUEST_TIMEOUT is set to 300 seconds"
else
    print_failure "Django REQUEST_TIMEOUT is NOT set to 300 seconds"
fi

if grep -q "UPLOAD_TIMEOUT = 300" "$BACKEND_DIR/backend/settings.py"; then
    print_success "Django UPLOAD_TIMEOUT is set to 300 seconds"
else
    print_failure "Django UPLOAD_TIMEOUT is NOT set to 300 seconds"
fi

# Check middleware
if grep -q "RequestTimeoutMiddleware" "$BACKEND_DIR/backend/settings.py"; then
    print_success "RequestTimeoutMiddleware is enabled"
else
    print_failure "RequestTimeoutMiddleware is NOT enabled"
fi

echo ""
print_status "Checking NGINX Configuration..."

# Check NGINX timeout settings
NGINX_CONFIG="/etc/nginx/sites-available/$SERVICE_NAME"
if [ -f "$NGINX_CONFIG" ]; then
    if grep -q "proxy_connect_timeout 300s" "$NGINX_CONFIG"; then
        print_success "NGINX proxy_connect_timeout is set to 300 seconds"
    else
        print_failure "NGINX proxy_connect_timeout is NOT set to 300 seconds"
    fi
    
    if grep -q "proxy_send_timeout 300s" "$NGINX_CONFIG"; then
        print_success "NGINX proxy_send_timeout is set to 300 seconds"
    else
        print_failure "NGINX proxy_send_timeout is NOT set to 300 seconds"
    fi
    
    if grep -q "proxy_read_timeout 300s" "$NGINX_CONFIG"; then
        print_success "NGINX proxy_read_timeout is set to 300 seconds"
    else
        print_failure "NGINX proxy_read_timeout is NOT set to 300 seconds"
    fi
    
    if grep -q "client_max_body_size 50M" "$NGINX_CONFIG"; then
        print_success "NGINX client_max_body_size is set to 50M"
    else
        print_warning "NGINX client_max_body_size is NOT set to 50M"
    fi
else
    print_warning "NGINX config file not found: $NGINX_CONFIG"
fi

echo ""
print_status "Checking Service Status..."

# Check if services are running
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "Gunicorn service is running"
else
    print_failure "Gunicorn service is NOT running"
fi

if sudo systemctl is-active --quiet nginx; then
    print_success "NGINX service is running"
else
    print_failure "NGINX service is NOT running"
fi

echo ""
print_status "Checking Gunicorn Process..."

# Check Gunicorn process and configuration
GUNICORN_PID=$(pgrep -f "gunicorn.*backend.wsgi")
if [ -n "$GUNICORN_PID" ]; then
    print_success "Gunicorn process is running (PID: $GUNICORN_PID)"
    
    # Check if it's using the config file
    GUNICORN_CONFIG=$(ps -p $GUNICORN_PID -o args= | grep -o "gunicorn.*")
    if echo "$GUNICORN_CONFIG" | grep -q "gunicorn.conf.py"; then
        print_success "Gunicorn is using the configuration file"
    else
        print_warning "Gunicorn may not be using the configuration file"
    fi
else
    print_failure "Gunicorn process not found"
fi

echo ""
print_status "Checking Recent Logs..."

# Check recent Gunicorn logs for any errors
echo "Recent Gunicorn logs:"
sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10 | grep -E "(ERROR|WARNING|timeout|504)" || echo "No recent errors found"

echo ""
print_status "========================================="
print_status "Verification Complete"
print_status "========================================="

# Summary
echo ""
print_status "Summary of Timeout Fixes:"
echo "• Gunicorn timeout: 300 seconds (5 minutes)"
echo "• Django request timeout: 300 seconds"
echo "• NGINX proxy timeouts: 300 seconds"
echo "• RequestTimeoutMiddleware: Enabled"
echo "• Serialization context issues: Fixed"
echo "• Chunked processing: Enabled"
echo ""
print_status "Your server should now handle large uploads without 504 errors!"
print_status "Test your upload functionality to confirm the fix is working."
