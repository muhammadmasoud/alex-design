# 🚀 Alex Design Deployment Guide for AWS Lightsail

## Prerequisites
- AWS Lightsail instance running Ubuntu
- SSH access to your instance
- Your project files ready for deployment

## 🎯 Quick Deployment Steps

### Step 1: Connect to Your Lightsail Instance
```bash
# Using your SSH key (Windows PowerShell)
ssh -i "your-key.pem" ubuntu@15.237.26.46
```

### Step 2: Upload Your Project Files
You have several options:

#### Option A: Using SCP (Recommended)
```bash
# From your local machine (Windows PowerShell)
scp -i "your-key.pem" -r . ubuntu@15.237.26.46:/home/ubuntu/alex-design
```

#### Option B: Using Git (if you have a repository)
```bash
# On the Lightsail instance
cd /home/ubuntu
git clone <your-repo-url> alex-design
```

#### Option C: Manual Upload via Lightsail Console
- Use the Lightsail console file manager to upload your files

### Step 3: Run the Deployment Script
```bash
# On the Lightsail instance
cd /home/ubuntu/alex-design
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Manual Deployment (Alternative)

If you prefer to deploy manually or the script fails:

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl
```

### 3. Install Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4. Set Up Application Directory
```bash
sudo mkdir -p /home/ubuntu/alex-design
sudo chown ubuntu:ubuntu /home/ubuntu/alex-design
cd /home/ubuntu/alex-design
```

### 5. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt
```

### 6. Configure PostgreSQL
```bash
sudo -u postgres psql -c "CREATE DATABASE alex_designs;"
sudo -u postgres psql -c "CREATE USER a7aa WITH PASSWORD 'admin';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE alex_designs TO a7aa;"
sudo -u postgres psql -c "ALTER USER a7aa CREATEDB;"
```

### 7. Configure Django
```bash
cd backend
export DJANGO_SETTINGS_MODULE=backend.settings_production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 8. Build Frontend
```bash
cd ../frontend
npm install
npm run build
```

### 9. Configure Nginx
```bash
sudo cp nginx.conf /etc/nginx/sites-available/alex-design
sudo ln -sf /etc/nginx/sites-available/alex-design /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 10. Set Up Django Service
```bash
cd ../backend
sudo cp alex-design.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alex-design
sudo systemctl start alex-design
```

## 🔍 Verification Steps

### Check Services Status
```bash
# Check Django service
sudo systemctl status alex-design

# Check Nginx service
sudo systemctl status nginx

# Check PostgreSQL service
sudo systemctl status postgresql
```

### Check Logs
```bash
# Django logs
sudo journalctl -u alex-design -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django application logs
tail -f /home/ubuntu/alex-design/backend/logs/django.log
```

### Test Your Application
- Frontend: http://15.237.26.46
- Django Admin: http://15.237.26.46/admin/
- API Endpoints: http://15.237.26.46/api/

## 🚨 Troubleshooting

### Common Issues

#### 1. Django Service Won't Start
```bash
# Check service status
sudo systemctl status alex-design

# Check logs
sudo journalctl -u alex-design -f

# Common fixes
sudo systemctl daemon-reload
sudo systemctl restart alex-design
```

#### 2. Nginx Configuration Error
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### 3. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
sudo -u postgres psql -d alex_designs -c "SELECT version();"
```

#### 4. Permission Issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/alex-design

# Fix permissions
chmod +x /home/ubuntu/alex-design/deploy.sh
```

### Port Issues
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Check what's using port 80
sudo netstat -tlnp | grep :80
```

## 🔒 Security Considerations

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS (if using SSL)
sudo ufw --force enable
```

### Database Security
- Change default passwords
- Restrict database access to localhost only
- Regular backups

### File Permissions
```bash
# Secure sensitive files
chmod 600 /home/ubuntu/alex-design/backend/.env
chmod 755 /home/ubuntu/alex-design/backend/media
```

## 📊 Monitoring

### System Resources
```bash
# Check system resources
htop
df -h
free -h
```

### Application Performance
```bash
# Check Django processes
ps aux | grep gunicorn

# Check Nginx processes
ps aux | grep nginx
```

## 🔄 Updates and Maintenance

### Update Application
```bash
cd /home/ubuntu/alex-design
git pull origin main  # if using git
# or upload new files manually

# Restart services
sudo systemctl restart alex-design
sudo systemctl restart nginx
```

### Backup Database
```bash
# Create backup
sudo -u postgres pg_dump alex_designs > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
sudo -u postgres psql alex_designs < backup_file.sql
```

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all services are running
3. Check file permissions and ownership
4. Ensure all dependencies are installed
5. Verify network configuration

## 🎉 Success!

Once deployed, your Alex Design portfolio will be accessible at:
- **Main Site**: http://15.237.26.46
- **Admin Panel**: http://15.237.26.46/admin/
- **API**: http://15.237.26.46/api/

Your application is now running in production on AWS Lightsail! 🚀
