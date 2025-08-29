#!/bin/bash

echo "🔧 Complete Gunicorn Service Fix for Alex Design"
echo "================================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Use sudo when prompted."
    exit 1
fi

# Function to check if service exists
service_exists() {
    systemctl list-unit-files | grep -q "^$1"
}

# Function to check if service is active
service_active() {
    systemctl is-active --quiet "$1"
}

echo "📋 Current status check..."
echo "-------------------------"

# Check existing services
if service_exists "gunicorn.service"; then
    echo "⚠️  Found old gunicorn.service - will remove"
else
    echo "✅ No old gunicorn.service found"
fi

if service_exists "alex-design.service"; then
    echo "⚠️  Found existing alex-design.service - will update"
else
    echo "✅ No existing alex-design.service found"
fi

echo ""
echo "🛑 Stopping and disabling old services..."
echo "----------------------------------------"

# Stop and disable any existing services
sudo systemctl stop gunicorn 2>/dev/null || true
sudo systemctl stop alex-design 2>/dev/null || true
sudo systemctl disable gunicorn 2>/dev/null || true
sudo systemctl disable alex-design 2>/dev/null || true

echo ""
echo "🗑️  Removing old service files..."
echo "--------------------------------"

# Remove old service files
sudo rm -f /etc/systemd/system/gunicorn.service
sudo rm -f /etc/systemd/system/alex-design.service

echo ""
echo "📁 Installing new service file..."
echo "--------------------------------"

# Copy the new service file
sudo cp backend/alex-design.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/alex-design.service

echo ""
echo "🔄 Reloading systemd..."
echo "----------------------"

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Enabling and starting new service..."
echo "-------------------------------------"

# Enable and start the new service
sudo systemctl enable alex-design
sudo systemctl start alex-design

echo ""
echo "⏳ Waiting for service to start..."
echo "--------------------------------"

# Wait a moment for the service to start
sleep 5

echo ""
echo "📊 Service Status Check..."
echo "------------------------"

# Check status
if service_active "alex-design"; then
    echo "✅ alex-design service is ACTIVE and running!"
else
    echo "❌ alex-design service failed to start"
    echo "📋 Checking logs for errors..."
    sudo journalctl -u alex-design --no-pager -n 20
    exit 1
fi

echo ""
echo "🔍 Detailed Service Status:"
echo "---------------------------"
sudo systemctl status alex-design --no-pager

echo ""
echo "📋 Service Information:"
echo "----------------------"
echo "Service name: alex-design"
echo "Status: $(systemctl is-active alex-design)"
echo "Enabled: $(systemctl is-enabled alex-design)"
echo "PID: $(systemctl show -p MainPID --value alex-design)"

echo ""
echo "🎯 Useful Commands:"
echo "------------------"
echo "📋 Check status: sudo systemctl status alex-design"
echo "📋 View logs: sudo journalctl -u alex-design -f"
echo "📋 Restart: sudo systemctl restart alex-design"
echo "📋 Stop: sudo systemctl stop alex-design"
echo "📋 Start: sudo systemctl start alex-design"

echo ""
echo "✅ Gunicorn service setup complete!"
echo "🌐 Your Django app should now be accessible at http://localhost:8000"
echo "🔗 Nginx will proxy requests from port 80 to port 8000"
