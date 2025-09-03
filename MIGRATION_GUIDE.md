# 🚀 Alex Design Migration to Hostinger KVM Server

## Server Details
- **New Server IP**: 72.60.81.174
- **OS**: Ubuntu 24.04 LTS
- **Resources**: 4GB RAM, 50GB Disk
- **Location**: Germany - Frankfurt

## 📋 Migration Steps

### STEP 1: Backup Current Server Data

#### 1.1 Connect to old server and backup database
```bash
ssh -i alex-design-key.pem ubuntu@52.47.162.66
```

#### 1.2 Create database backup
```bash
cd /home/ubuntu/alex-design/backend
source venv/bin/activate
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > full_backup_$(date +%Y%m%d_%H%M%S).json
```

#### 1.3 Backup media files
```bash
cd /home/ubuntu/alex-design/backend
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

#### 1.4 Download backups to local machine
```bash
# Exit from server first
exit

# Download database backup (run from your local machine)
scp -i alex-design-key.pem ubuntu@52.47.162.66:/home/ubuntu/alex-design/backend/full_backup_*.json ./

# Download media backup
scp -i alex-design-key.pem ubuntu@52.47.162.66:/home/ubuntu/alex-design/backend/media_backup_*.tar.gz ./
```

### STEP 2: Setup New Hostinger Server

#### 2.1 Connect to new server
```bash
ssh root@72.60.81.174
```

#### 2.2 Initial server setup
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl software-properties-common ufw

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Create ubuntu user (if doesn't exist)
adduser ubuntu
usermod -aG sudo ubuntu
mkdir -p /home/ubuntu/.ssh
cp /root/.ssh/authorized_keys /home/ubuntu/.ssh/
chown -R ubuntu:ubuntu /home/ubuntu/.ssh
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys

# Switch to ubuntu user
su - ubuntu
```

#### 2.3 Setup PostgreSQL
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE alex_designs;
CREATE USER alex_designs WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE alex_designs TO alex_designs;
ALTER USER alex_designs CREATEDB;
\q
```

#### 2.4 Setup application directory
```bash
mkdir -p /home/ubuntu/alex-design
cd /home/ubuntu/alex-design
```

### STEP 3: Upload Code and Restore Data

#### 3.1 Upload your code (from your local machine)
```bash
# Upload the entire project
scp -r -i alex-design-key.pem D:\Projects\alex-design ubuntu@72.60.81.174:/home/ubuntu/

# OR clone from your repository if it's on GitHub
ssh ubuntu@72.60.81.174
cd /home/ubuntu/alex-design
git clone https://github.com/muhammadmasoud/alex-design.git .
```

#### 3.2 Upload backup files (from your local machine)
```bash
scp -i alex-design-key.pem full_backup_*.json ubuntu@72.60.81.174:/home/ubuntu/alex-design/backend/
scp -i alex-design-key.pem media_backup_*.tar.gz ubuntu@72.60.81.174:/home/ubuntu/alex-design/backend/
```

### STEP 4: Setup Backend

#### 4.1 Connect to new server as ubuntu user
```bash
ssh ubuntu@72.60.81.174
cd /home/ubuntu/alex-design/backend
```

#### 4.2 Update environment file for new server
```bash
# Edit the .env file
nano .env
```

Update these values in .env:
```env
# Change IP address
ALLOWED_HOSTS=72.60.81.174,localhost,127.0.0.1

# Update CSRF trusted origins
CSRF_TRUSTED_ORIGINS=http://72.60.81.174,https://72.60.81.174
```

#### 4.3 Setup Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4.4 Run Django setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load your backed up data
python manage.py loaddata full_backup_*.json

# Extract media files
tar -xzf media_backup_*.tar.gz

# Collect static files
python manage.py collectstatic --noinput
```

### STEP 5: Setup Frontend

#### 5.1 Build frontend
```bash
cd /home/ubuntu/alex-design/frontend
npm install
npm run build
```

### STEP 6: Configure Nginx

#### 6.1 Update Nginx configuration
```bash
# Copy nginx config
sudo cp /home/ubuntu/alex-design/nginx.conf /etc/nginx/sites-available/alex-design

# Update the config for new server
sudo nano /etc/nginx/sites-available/alex-design
```

Update IP addresses in nginx.conf (change 52.47.162.66 to 72.60.81.174 if any exist).

#### 6.2 Enable site
```bash
sudo ln -sf /etc/nginx/sites-available/alex-design /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### STEP 7: Setup Django Service

#### 7.1 Configure systemd service
```bash
sudo cp /home/ubuntu/alex-design/backend/alex-design.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alex-design
sudo systemctl start alex-design
```

### STEP 8: Configure Firewall

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

### STEP 9: Test Your Application

#### 9.1 Check services
```bash
# Check Django service
sudo systemctl status alex-design

# Check Nginx
sudo systemctl status nginx

# Check if site is accessible
curl http://72.60.81.174
```

#### 9.2 Access your application
- **Frontend**: http://72.60.81.174
- **Admin**: http://72.60.81.174/admin/
- **API**: http://72.60.81.174/api/

### STEP 10: Verify Data Migration

#### 10.1 Login to admin panel
Go to http://72.60.81.174/admin/ and verify:
- All projects are there
- All services are there
- All images are displaying
- Categories are intact
- Users can login

### STEP 11: Update DNS (Optional)

If you have a domain name, update your DNS records to point to the new IP: `72.60.81.174`

## 🔧 Troubleshooting Commands

### Check logs
```bash
# Django logs
sudo journalctl -u alex-design -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python
ps aux | grep nginx
```

### Restart services
```bash
sudo systemctl restart alex-design
sudo systemctl restart nginx
```

### Database connection test
```bash
cd /home/ubuntu/alex-design/backend
source venv/bin/activate
python manage.py shell
```

In Django shell:
```python
from portfolio.models import Project, Service
print(f"Projects: {Project.objects.count()}")
print(f"Services: {Service.objects.count()}")
```

## 📝 Important Notes

1. **Keep your old server running** until you've confirmed everything works on the new server
2. **Test thoroughly** before switching DNS or promoting the new server
3. **The new server IP is 72.60.81.174** - update this in your local SSH config if needed
4. **Your data will be preserved** through the JSON backup and restore process
5. **Media files** (images) will be restored from the tar.gz backup

## 🚨 Security Reminders

After migration, consider:
- Changing default passwords
- Setting up SSL certificate
- Updating secret keys
- Configuring automated backups

Let me know if you encounter any issues during the migration!
