# Media Files Troubleshooting Guide

## Problem Description
Images uploaded through the admin dashboard work locally but don't appear on the Ubuntu server.

## Root Causes Identified

### 1. **Nginx Configuration Issues**
- Media files path mismatch between nginx and Django
- Missing proper file type handling for images
- Incorrect file permissions

### 2. **Django Settings Issues**
- Relative paths in production settings
- Missing production-specific media configuration
- File upload permissions not properly set

### 3. **File System Issues**
- Media directories may not exist
- Incorrect ownership and permissions
- Missing subdirectories for projects and services

## Solutions Applied

### 1. **Updated nginx.conf**
- Fixed media files path to `/home/ubuntu/alex-design/backend/media/`
- Added proper image file handling
- Enhanced caching and security headers

### 2. **Created settings_production.py**
- Absolute paths for MEDIA_ROOT and STATIC_ROOT
- Production-specific file upload settings
- Proper logging configuration

### 3. **Created fix_media_files.sh**
- Automated script to fix permissions
- Creates missing directories
- Sets proper ownership and permissions

## Deployment Steps

### Step 1: Upload Fixed Files
```bash
# Upload these files to your Ubuntu server:
# - nginx.conf (updated)
# - backend/backend/settings_production.py (new)
# - fix_media_files.sh (new)
```

### Step 2: Run the Fix Script
```bash
# SSH into your Ubuntu server
ssh ubuntu@52.47.162.66

# Navigate to project directory
cd /home/ubuntu/alex-design

# Make the script executable
chmod +x fix_media_files.sh

# Run the fix script
./fix_media_files.sh
```

### Step 3: Update Django Service
```bash
# Edit the Django service file
sudo nano /etc/systemd/system/alex-design.service

# Update the environment variable to use production settings
Environment=DJANGO_SETTINGS_MODULE=backend.settings_production

# Reload and restart the service
sudo systemctl daemon-reload
sudo systemctl restart alex-design
```

### Step 4: Test the Fix
1. **Upload a test image** through the admin dashboard
2. **Check the media URL**: `http://52.47.162.66/media/projects/your_image.jpg`
3. **Verify the image displays** on your website

## Verification Commands

### Check Media Directory Structure
```bash
ls -la /home/ubuntu/alex-design/backend/media/
ls -la /home/ubuntu/alex-design/backend/media/projects/
ls -la /home/ubuntu/alex-design/backend/media/services/
```

### Check File Permissions
```bash
# Should show 755 for directories, 644 for files
ls -la /home/ubuntu/alex-design/backend/media/
```

### Check Nginx Configuration
```bash
sudo nginx -t
sudo systemctl status nginx
```

### Check Django Service
```bash
sudo systemctl status alex-design
sudo journalctl -u alex-design -f
```

## Common Issues and Solutions

### Issue: "Permission denied" errors
**Solution**: Run the fix script to set proper permissions

### Issue: Images still not loading
**Solution**: Check nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Issue: Django can't write to media directory
**Solution**: Ensure ownership is `ubuntu:ubuntu` and permissions are `755`

### Issue: 404 errors for media files
**Solution**: Verify nginx location block is correct and media directory exists

## File Structure After Fix
```
/home/ubuntu/alex-design/
├── backend/
│   ├── media/
│   │   ├── projects/          # Project images
│   │   └── services/          # Service icons
│   ├── staticfiles/           # Collected static files
│   └── logs/                  # Django logs
└── nginx.conf                 # Updated nginx configuration
```

## Testing Checklist
- [ ] Media directories exist with proper permissions
- [ ] Nginx configuration test passes
- [ ] Django service is running with production settings
- [ ] Test image upload works in admin dashboard
- [ ] Test image is accessible via direct URL
- [ ] Test image displays on website

## Support
If issues persist after following this guide:
1. Check Django logs: `tail -f /home/ubuntu/alex-design/backend/logs/django.log`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify file paths and permissions
4. Ensure Django is using production settings
