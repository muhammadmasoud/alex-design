# Production Deployment Checklist for Alex Design Portfolio

## Local Development Completed ✅

### Backend Optimizations
- [x] Added image optimization utilities (`image_utils.py`)
- [x] Updated signals for automatic image compression
- [x] Enhanced serializers to return full URLs
- [x] Optimized settings for production
- [x] Added management command for batch image optimization
- [x] Updated Gunicorn configuration for better performance
- [x] Created optimized NGINX configuration
- [x] Added pillow-heif for HEIC support

### Files Modified/Created
- [x] `portfolio/image_utils.py` - Image optimization functions
- [x] `portfolio/signals.py` - Auto-optimization on upload
- [x] `portfolio/serializers.py` - Full URL support
- [x] `backend/settings.py` - Production optimizations
- [x] `portfolio/management/commands/optimize_images.py` - Batch optimization
- [x] `gunicorn.conf.py` - Production configuration
- [x] `nginx.conf` - Optimized web server config
- [x] `deploy-production.sh` - Automated deployment script
- [x] `requirements.txt` - Added pillow-heif
- [x] `FRONTEND_OPTIMIZATION.md` - Frontend optimization guide

## AWS Lightsail Server Deployment Steps

### Step 1: Push Changes to Git
```bash
# On your local machine
git add .
git commit -m "Production optimization: image compression, NGINX config, deployment automation"
git push origin main
```

### Step 2: Pull Changes on Server
```bash
# SSH into your Lightsail server
ssh ubuntu@52.47.162.66

# Navigate to project and pull changes
cd /home/ubuntu/alex-design
git pull origin main
```

### Step 3: Run Deployment Script
```bash
# Make deployment script executable
chmod +x deploy-production.sh

# Run the deployment script
./deploy-production.sh
```

### Step 4: Manual Verification (if script fails)

#### Install Dependencies
```bash
cd /home/ubuntu/alex-design/backend
source ../venv/bin/activate
pip install -r requirements.txt
```

#### Run Migrations
```bash
python manage.py migrate
```

#### Optimize Existing Images (Optional but Recommended)
```bash
# Check what images need optimization
python manage.py optimize_images --dry-run

# Optimize images (will take time depending on number of images)
python manage.py optimize_images --batch-size=5
```

#### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### Update NGINX Configuration
```bash
# Copy the new nginx config
sudo cp nginx.conf /etc/nginx/sites-available/alex-design

# Enable the site (if not already enabled)
sudo ln -sf /etc/nginx/sites-available/alex-design /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test NGINX configuration
sudo nginx -t

# Restart NGINX
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### Setup/Restart Gunicorn Service
```bash
# Create systemd service file
sudo tee /etc/systemd/system/alex-design.service > /dev/null <<EOF
[Unit]
Description=Alex Design Gunicorn daemon
Requires=alex-design.socket
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
RuntimeDirectory=gunicorn
WorkingDirectory=/home/ubuntu/alex-design/backend
Environment="DJANGO_ENV=production"
Environment="PRODUCTION=true"
Environment="LIGHTSAIL=true"
ExecStart=/home/ubuntu/alex-design/venv/bin/gunicorn --config gunicorn.conf.py backend.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable alex-design
sudo systemctl start alex-design
sudo systemctl status alex-design
```

#### Set Proper Permissions
```bash
cd /home/ubuntu/alex-design/backend
sudo chown -R ubuntu:ubuntu media/
sudo chmod -R 755 media/
sudo chown -R ubuntu:ubuntu staticfiles/
sudo chmod -R 755 staticfiles/

# Create media directories if they don't exist
mkdir -p media/projects/albums
mkdir -p media/services/albums
```

## Frontend Optimizations (Optional)

### If you have a React frontend to build:
```bash
cd /home/ubuntu/alex-design/frontend
npm install
npm run build

# Copy build files to Django static
sudo rm -rf /home/ubuntu/alex-design/backend/staticfiles/frontend
sudo mkdir -p /home/ubuntu/alex-design/backend/staticfiles/frontend
sudo cp -r dist/* /home/ubuntu/alex-design/backend/staticfiles/frontend/
sudo chown -R ubuntu:ubuntu /home/ubuntu/alex-design/backend/staticfiles
```

## Post-Deployment Verification

### Check Service Status
```bash
# Check Gunicorn
sudo systemctl status alex-design

# Check NGINX
sudo systemctl status nginx

# Check if website responds
curl -I http://52.47.162.66/
curl -I http://52.47.162.66/api/projects/
```

### Monitor Logs
```bash
# Watch Gunicorn logs
sudo journalctl -u alex-design -f

# Watch NGINX logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Test Image Upload
1. Go to `http://52.47.162.66/admin/`
2. Login and try uploading a large image
3. Verify it gets optimized automatically
4. Check that images load properly on the frontend

## Performance Monitoring

### System Resources
```bash
# Monitor memory and CPU
htop

# Monitor disk I/O
sudo iotop

# Check disk space
df -h

# Check image optimization results
ls -lah /home/ubuntu/alex-design/backend/media/projects/
```

### Database Optimization (After Image Migration)
```bash
# If you had images stored in database before, clean up
# This is optional since your images are already stored as files
cd /home/ubuntu/alex-design/backend
python manage.py shell

# In Python shell:
# from django.db import connection
# cursor = connection.cursor()
# cursor.execute("VACUUM FULL;")  # PostgreSQL only
# cursor.execute("ANALYZE;")
```

## Security Checklist

- [x] DEBUG = False in production
- [x] ALLOWED_HOSTS properly configured
- [x] CSRF protection enabled
- [x] CORS properly configured
- [x] File upload size limits set
- [x] Rate limiting configured in NGINX
- [x] Security headers added
- [ ] SSL/HTTPS setup (optional for future)
- [ ] Database backups configured
- [ ] Log rotation configured

## Troubleshooting

### Common Issues:

1. **Images not loading**: Check NGINX media location and permissions
2. **Large uploads failing**: Verify NGINX client_max_body_size and Django settings
3. **Service won't start**: Check logs with `sudo journalctl -u alex-design`
4. **Permission errors**: Run `sudo chown -R ubuntu:ubuntu /home/ubuntu/alex-design`

### Emergency Rollback:
```bash
# Stop services
sudo systemctl stop alex-design nginx

# Restore from backup (if you made one)
# Or revert git changes:
cd /home/ubuntu/alex-design
git log --oneline  # Find previous commit
git reset --hard <previous-commit-hash>

# Restart services
sudo systemctl start alex-design nginx
```

## Success Indicators

✅ Website loads at http://52.47.162.66/  
✅ Admin panel accessible at http://52.47.162.66/admin/  
✅ Images upload and display properly  
✅ Images are automatically optimized on upload  
✅ API endpoints respond correctly  
✅ No server errors in logs  
✅ System resources usage is reasonable  

## Next Steps (Optional Future Improvements)

1. **SSL/HTTPS Setup**: Use Let's Encrypt with certbot
2. **CDN**: Setup CloudFlare or AWS CloudFront
3. **Database Backups**: Automated PostgreSQL backups
4. **Monitoring**: Setup monitoring with tools like Uptime Robot
5. **Caching**: Add Redis for session and cache storage
6. **Load Balancing**: If traffic grows significantly

---

**After completing deployment, your portfolio will be optimized for:**
- Fast image loading with automatic compression
- Better SEO and performance scores
- Reduced server load and bandwidth usage
- Improved user experience with faster page loads
- Production-ready security and performance settings
