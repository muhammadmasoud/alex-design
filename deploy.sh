#!/bin/bash

# Alex Design Deployment Script for AWS Lightsail
# This script will deploy your Django + React application

set -e  # Exit on any error

echo "🚀 Starting Alex Design deployment on AWS Lightsail..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing required system packages..."
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl

# Install Node.js and npm (for frontend build)
echo "📱 Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /home/ubuntu/alex-design
sudo chown ubuntu:ubuntu /home/ubuntu/alex-design
cd /home/ubuntu/alex-design

# Clone your repository (replace with your actual git repo if you have one)
# git clone <your-repo-url> .
# For now, we'll assume the code is already uploaded

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements_production.txt

# Set up PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE alex_designs;"
sudo -u postgres psql -c "CREATE USER a7aa WITH PASSWORD 'admin';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE alex_designs TO a7aa;"
sudo -u postgres psql -c "ALTER USER a7aa CREATEDB;"

# Navigate to backend directory
cd backend

# Set production environment
export DJANGO_SETTINGS_MODULE=backend.settings_production

# Run Django migrations
echo "🔄 Running Django migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (you'll need to provide credentials)
echo "👤 Creating superuser..."
echo "Please create your superuser account:"
python manage.py createsuperuser

# Build frontend
echo "🏗️ Building frontend..."
cd ../frontend
npm install
npm run build

# Set up Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/alex-design
sudo ln -sf /etc/nginx/sites-available/alex-design /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Set up Django service
echo "⚙️ Setting up Django service..."
cd ../backend
sudo cp alex-design.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alex-design
sudo systemctl start alex-design

# Set up firewall (if not already configured)
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create logs directory
sudo mkdir -p /home/ubuntu/alex-design/backend/logs
sudo chown ubuntu:ubuntu /home/ubuntu/alex-design/backend/logs

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should now be accessible at: http://15.237.26.46"
echo "🔧 Django admin: http://15.237.26.46/admin/"
echo "📊 Check service status: sudo systemctl status alex-design"
echo "📝 Check logs: sudo journalctl -u alex-design -f"
