# 🚀 AWS LIGHTSAIL DEPLOYMENT GUIDE

## Overview
This guide covers deploying the optimized Alex Design portfolio application to AWS Lightsail with all performance and security enhancements.

## 🔧 Production Optimizations Applied

### Backend Optimizations
- ✅ Database indexing for optimal query performance
- ✅ Production-ready logging configuration
- ✅ Security headers middleware
- ✅ Performance monitoring middleware
- ✅ Proper environment variable management
- ✅ Optimized file upload handling

### Frontend Optimizations
- ✅ Removed unused dependencies (react-lazy-load-image-component)
- ✅ Optimized bundle splitting for better caching
- ✅ Production console.log removal
- ✅ TypeScript strict mode enabled
- ✅ Lazy loading for admin components

### Security Enhancements
- ✅ Content Security Policy headers
- ✅ XSS protection headers
- ✅ CSRF protection
- ✅ Referrer policy configuration
- ✅ Permissions policy
- ✅ Secure cookie settings for production

## � AWS LIGHTSAIL DEPLOYMENT COMMANDS

### Step 1: Connect to Your Server
```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

### Step 2: Navigate to Project Directory
```bash
cd /home/ubuntu/alex-design
```

### Step 3: Backup Current State (Safety First!)
```bash
# Backup database
sudo -u postgres pg_dump alex_designs > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/media/

# Backup current code (in case rollback needed)
cp -r . ../alex-design-backup-$(date +%Y%m%d_%H%M%S)
```

### Step 4: Pull Latest Optimized Code
```bash
git stash  # Save any local changes
git pull origin main
```

### Step 5: Update Backend Dependencies & Apply Optimizations
```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies (if any were added)
pip install -r requirements.txt

# Apply database migrations for new indexes
python manage.py migrate

# Collect static files with optimizations
python manage.py collectstatic --noinput --clear
```

### Step 6: Update Frontend with Optimizations
```bash
cd ../frontend

# Install dependencies (this will automatically remove unused packages)
npm install

# Build optimized production bundle
npm run build
```

### Step 7: Update Nginx Configuration (if needed)
```bash
# Check if nginx config needs updating
sudo nginx -t

# If all good, reload nginx
sudo systemctl reload nginx
```

### Step 8: Restart Django Application
```bash
# Restart your Django service (replace with your actual service name)
sudo systemctl restart alex-design

# Check service status
sudo systemctl status alex-design

# Check logs to ensure everything started correctly
sudo journalctl -u alex-design -f --lines=50
```

### Step 9: Verify Deployment
```bash
# Check if application is responding
curl -I http://your-domain.com

# Check Django admin is accessible
curl -I http://your-domain.com/admin/

# Check API endpoints
curl -I http://your-domain.com/api/projects/
```

### Step 10: Performance & Security Verification
```bash
# Check new security headers are applied
curl -I http://your-domain.com | grep -E "(X-Content-Type-Options|X-Frame-Options|Content-Security-Policy)"

# Check response times (should be faster with optimizations)
curl -w "%{time_total}\n" -o /dev/null -s http://your-domain.com

# Monitor application logs for performance middleware
sudo journalctl -u alex-design -f | grep "Performance\|Response-Time"
```

## 🔧 Optional: Environment Variables Update

If you want to add the new environment template:
```bash
cd backend

# Create production environment template
cat > .env.production.template << 'EOF'
# Production Environment Variables Template
DJANGO_ENV=production
PRODUCTION=true
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alex_designs
DB_USER=alex_designs
DB_PASSWORD=your-secure-database-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CONTACT_EMAIL=contact@yourdomain.com
EOF
```

## 🔒 Security Checklist

- [ ] Environment variables configured
- [ ] Secret key is strong and unique
- [ ] Debug mode disabled in production
- [ ] HTTPS configured with valid SSL certificate
- [ ] Database credentials secured
- [ ] File upload limits configured
- [ ] CORS origins restricted to your domain
- [ ] Admin interface protected
- [ ] Regular backups configured

## 📊 Performance Monitoring

### Built-in Monitoring
- Performance middleware tracks slow requests
- Response time headers added
- API endpoint performance tracking
- Automatic error logging

### Recommended External Tools
- **Application Performance:** New Relic, DataDog
- **Uptime Monitoring:** Pingdom, UptimeRobot
- **Error Tracking:** Sentry
- **Log Management:** ELK Stack, Splunk

## 🔄 Maintenance

### Database Backups
```bash
# Create backup
pg_dump alex_designs > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql alex_designs < backup_file.sql
```

### Media Files Backup
```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/media/
```

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart alex-design
sudo systemctl restart nginx
```

## 🚨 Troubleshooting

## 🚨 If You Encounter Issues

### Django Service Won't Start
```bash
# Check detailed error logs
sudo journalctl -u alex-design -e

# Check Django syntax
cd /home/ubuntu/alex-design/backend
source venv/bin/activate
python manage.py check

# Test Django manually
python manage.py runserver 0.0.0.0:8000
```

### Frontend Build Issues
```bash
cd /home/ubuntu/alex-design/frontend

# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database Migration Issues
```bash
cd /home/ubuntu/alex-design/backend
source venv/bin/activate

# Check migration status
python manage.py showmigrations

# If needed, fake apply specific migration
python manage.py migrate --fake-initial
```

### Performance Issues
```bash
# Monitor real-time performance
sudo journalctl -u alex-design -f | grep "Performance\|Error"

# Check system resources
htop
df -h
free -m
```

## 📊 Monitoring Your Optimizations

### Check Bundle Size Improvements
```bash
# Check new frontend bundle sizes
ls -lah /home/ubuntu/alex-design/frontend/dist/assets/js/
```

### Monitor Database Performance
```bash
# Check if new indexes are being used
sudo -u postgres psql alex_designs -c "
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
ORDER BY idx_tup_read DESC;"
```

### Security Headers Verification
```bash
# Test security headers are working
curl -I http://your-domain.com | grep -E "(X-Content-Type|X-Frame|Content-Security|Referrer-Policy)"
```

## 📞 Support

For deployment issues or questions:
1. Check the application logs
2. Review this documentation
3. Check GitHub issues
4. Contact the development team

## 🔄 Version History

- **v1.0** - Initial production deployment guide
- **v1.1** - Added Docker deployment option
- **v1.2** - Enhanced security and performance optimizations
