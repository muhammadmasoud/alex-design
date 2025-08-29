#!/bin/bash

echo "🔧 Fixing Gunicorn Service Issues..."

# Stop the broken service
echo "Stopping broken gunicorn service..."
sudo systemctl stop gunicorn 2>/dev/null || true
sudo systemctl stop alex-design 2>/dev/null || true

# Disable the broken service
echo "Disabling broken services..."
sudo systemctl disable gunicorn 2>/dev/null || true
sudo systemctl disable alex-design 2>/dev/null || true

# Remove old service files
echo "Removing old service files..."
sudo rm -f /etc/systemd/system/gunicorn.service
sudo rm -f /etc/systemd/system/alex-design.service

# Copy the new service file
echo "Installing new service file..."
sudo cp backend/alex-design.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/alex-design.service

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start the new service
echo "Starting new alex-design service..."
sudo systemctl enable alex-design
sudo systemctl start alex-design

# Check status
echo "Checking service status..."
sudo systemctl status alex-design

echo ""
echo "✅ Gunicorn service should now be working!"
echo "📋 To check status: sudo systemctl status alex-design"
echo "📋 To view logs: sudo journalctl -u alex-design -f"
echo "📋 To restart: sudo systemctl restart alex-design"
