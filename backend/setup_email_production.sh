#!/bin/bash

# Alex Design Email Setup Script for Ubuntu Production Server
# Run this script on your Ubuntu server to configure email

echo "🏗️ Alex Design - Production Email Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should NOT be run as root${NC}"
   echo "Switch to ubuntu user: sudo -u ubuntu bash"
   exit 1
fi

# Check if we're in the right directory
if [[ ! -f "manage.py" ]]; then
    echo -e "${RED}❌ Error: manage.py not found${NC}"
    echo "Please run this script from the Django backend directory:"
    echo "cd /home/ubuntu/alex-design/backend"
    exit 1
fi

echo -e "${BLUE}📧 Email Configuration Setup${NC}"
echo ""

# Check if .env already exists
if [[ -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to backup and recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo -e "${GREEN}✅ Backed up existing .env file${NC}"
    else
        echo -e "${YELLOW}⚠️  Keeping existing .env file${NC}"
        echo "You can manually edit it or run this script again"
        exit 0
    fi
fi

# Collect email credentials
echo -e "${BLUE}Please provide your email configuration:${NC}"
echo ""

read -p "Gmail address (e.g., mohamedaboelhamd765@gmail.com): " EMAIL_USER
read -p "Gmail App Password (16 characters): " EMAIL_PASSWORD
read -p "Contact email (where to receive messages): " CONTACT_EMAIL

# Generate a secret key
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Create .env file
cat > .env << EOF
# Django Production Environment Variables
SECRET_KEY=$SECRET_KEY
DEBUG=False
DJANGO_ENV=production
PRODUCTION=true

# Database Configuration
DB_NAME=alex_designs
DB_USER=a7aa
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Email Configuration - CRITICAL FOR CONTACT FORM
EMAIL_HOST_USER=$EMAIL_USER
EMAIL_HOST_PASSWORD=$EMAIL_PASSWORD
DEFAULT_FROM_EMAIL=noreply@alexdesign.com
CONTACT_EMAIL=$CONTACT_EMAIL

# Production Settings
ALLOWED_HOSTS=52.47.162.66,2a05:d012:18a:1600:539:6792:3ed7:c389

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
EOF

# Set proper permissions
chmod 600 .env

echo -e "${GREEN}✅ .env file created successfully${NC}"
echo ""

# Test email configuration
echo -e "${BLUE}🧪 Testing email configuration...${NC}"
python manage.py test_email --to "$CONTACT_EMAIL"

if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✅ Email test completed${NC}"
    echo -e "${YELLOW}📧 Check your email inbox (and spam folder)${NC}"
    echo ""
    
    # Restart services
    echo -e "${BLUE}🔄 Restarting services...${NC}"
    sudo systemctl restart alex-design
    sudo systemctl restart nginx
    
    echo -e "${GREEN}✅ Services restarted${NC}"
    echo ""
    echo -e "${GREEN}🎉 Email setup completed successfully!${NC}"
    echo "Your contact form should now work properly."
    echo ""
    echo -e "${BLUE}📊 To check service status:${NC}"
    echo "sudo systemctl status alex-design"
    echo ""
    echo -e "${BLUE}📋 To view logs:${NC}"
    echo "sudo journalctl -u alex-design -f"
    
else
    echo ""
    echo -e "${RED}❌ Email test failed${NC}"
    echo -e "${YELLOW}📖 Please check the PRODUCTION_EMAIL_SETUP.md guide${NC}"
    echo ""
    echo -e "${BLUE}Common issues:${NC}"
    echo "1. Make sure you're using Gmail App Password (not regular password)"
    echo "2. Enable 2-Factor Authentication on Gmail"
    echo "3. Check that the Gmail account is correct"
fi

echo ""
echo -e "${BLUE}📚 For more help, see:${NC}"
echo "- PRODUCTION_EMAIL_SETUP.md"
echo "- Run: python manage.py test_email --debug"
