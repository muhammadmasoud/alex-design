#!/bin/bash

# Production Deployment Script for Alex Design Portfolio
# This script should be run on your AWS Lightsail server after git pull

set -e  # Exit on any error

echo "========================================="
echo "Starting Alex Design Production Deployment"
echo "========================================="

# Configuration
PROJECT_DIR="/home/ubuntu/alex-design"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="alex-design"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Step 1: Backup current state
print_status "Creating backup of current deployment..."
sudo systemctl stop "$SERVICE_NAME" || print_warning "Service not running"
sudo systemctl stop nginx || print_warning "Nginx not running"

# Step 2: Activate virtual environment and install dependencies
print_status "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
cd "$BACKEND_DIR"

# Install new packages
pip install -r requirements.txt

# Step 3: Database migrations
print_status "Running database migrations..."
python manage.py migrate

# Step 4: Optimize existing images (if needed)
print_status "Checking for images that need optimization..."
python manage.py optimize_images --dry-run

read -p "Do you want to optimize existing images? This may take some time. (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Optimizing images for production..."
    python manage.py optimize_images --batch-size=5
else
    print_status "Skipping image optimization"
fi

# Step 5: Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Step 6: Build frontend (if needed)
if [ -d "$FRONTEND_DIR" ]; then
    print_status "Building frontend..."
    cd "$FRONTEND_DIR"
    
    # Check if package.json exists
    if [ -f "package.json" ]; then
        # Install dependencies if node_modules doesn't exist or package.json changed
        if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
            print_status "Installing frontend dependencies..."
            npm install
        fi
        
        # Build production version
        print_status "Building production frontend..."
        npm run build
        
        # Copy built files to Django static directory
        if [ -d "dist" ]; then
            print_status "Copying frontend build to Django static files..."
            sudo rm -rf "$BACKEND_DIR/staticfiles/frontend"
            sudo mkdir -p "$BACKEND_DIR/staticfiles/frontend"
            sudo cp -r dist/* "$BACKEND_DIR/staticfiles/frontend/"
            sudo chown -R ubuntu:ubuntu "$BACKEND_DIR/staticfiles"
        fi
    fi
fi

# Step 7: Set correct permissions
print_status "Setting correct file permissions..."
cd "$BACKEND_DIR"
sudo chown -R ubuntu:ubuntu media/
sudo chmod -R 755 media/
sudo chown -R ubuntu:ubuntu staticfiles/
sudo chmod -R 755 staticfiles/

# Make sure uploads directory exists
mkdir -p media/projects
mkdir -p media/services
mkdir -p media/projects/albums
mkdir -p media/services/albums

# Step 8: Update Gunicorn configuration if needed
print_status "Checking Gunicorn configuration..."
if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    print_status "Creating Gunicorn service file..."
    sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null <<EOF
[Unit]
Description=Alex Design Gunicorn daemon
Requires=$SERVICE_NAME.socket
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
RuntimeDirectory=gunicorn
WorkingDirectory=$BACKEND_DIR
Environment="DJANGO_ENV=production"
Environment="PRODUCTION=true"
Environment="LIGHTSAIL=true"
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
fi

# Step 9: Update NGINX configuration if needed
print_status "Checking NGINX configuration..."
NGINX_CONFIG="/etc/nginx/sites-available/$SERVICE_NAME"
if [ ! -f "$NGINX_CONFIG" ]; then
    print_status "Creating NGINX configuration..."
    sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name 52.47.162.66 2a05:d012:18a:1600:539:6792:3ed7:c389;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Static files
    location /static/ {
        alias $BACKEND_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $BACKEND_DIR/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for large uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Increase buffer size for large responses
        proxy_buffer_size 16k;
        proxy_buffers 8 16k;
    }

    # Increase client body size for file uploads
    client_max_body_size 25M;
}
EOF

    sudo ln -sf "$NGINX_CONFIG" "/etc/nginx/sites-enabled/"
    sudo rm -f "/etc/nginx/sites-enabled/default"
fi

# Step 10: Start services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl start "$SERVICE_NAME"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart nginx
sudo systemctl enable nginx

# Step 11: Check service status
print_status "Checking service status..."
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

# Step 12: Final checks
print_status "Running final checks..."

# Check if website is responding
if curl -f -s http://localhost:80/ > /dev/null; then
    print_status "✓ Website is responding"
else
    print_warning "✗ Website may not be responding properly"
fi

# Display resource usage
print_status "Current system resource usage:"
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h /
echo ""

print_status "========================================="
print_status "Deployment completed successfully!"
print_status "========================================="
print_status "Your portfolio is now running at:"
print_status "http://52.47.162.66"
print_status ""
print_status "Logs can be viewed with:"
print_status "sudo journalctl -u $SERVICE_NAME -f"
print_status "sudo tail -f /var/log/nginx/access.log"
print_status "sudo tail -f /var/log/nginx/error.log"
print_status ""
print_status "To monitor the system:"
print_status "htop (install with: sudo apt install htop)"
print_status "sudo iotop (install with: sudo apt install iotop)"
