# ✅ Alex Design Deployment Checklist

## Before You Start
- [ ] AWS Lightsail instance is running
- [ ] You have SSH access to your instance
- [ ] Your project files are ready
- [ ] You have your SSH key file (.pem)

## Step 1: Upload Files
- [ ] Run the PowerShell upload script: `.\upload_to_lightsail.ps1 -KeyPath "path\to\your\key.pem"`
- [ ] Verify files were uploaded successfully

## Step 2: Connect to Instance
- [ ] SSH into your instance: `ssh -i "your-key.pem" ubuntu@15.237.26.46`
- [ ] Navigate to project directory: `cd /home/ubuntu/alex-design`

## Step 3: Deploy
- [ ] Make deployment script executable: `chmod +x deploy.sh`
- [ ] Run deployment script: `./deploy.sh`
- [ ] Follow the prompts (create superuser, etc.)

## Step 4: Verify Deployment
- [ ] Check Django service: `sudo systemctl status alex-design`
- [ ] Check Nginx service: `sudo systemctl status nginx`
- [ ] Check PostgreSQL service: `sudo systemctl status postgresql`
- [ ] Test frontend: http://15.237.26.46
- [ ] Test admin panel: http://15.237.26.46/admin/
- [ ] Test API: http://15.237.26.46/api/

## Step 5: Security
- [ ] Change default database passwords
- [ ] Update Django secret key
- [ ] Configure firewall rules
- [ ] Set up SSL certificate (optional but recommended)

## Troubleshooting Commands
```bash
# Check service logs
sudo journalctl -u alex-design -f
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart alex-design
sudo systemctl restart nginx

# Check file permissions
ls -la /home/ubuntu/alex-design/
sudo chown -R ubuntu:ubuntu /home/ubuntu/alex-design/
```

## Success Indicators
- ✅ Frontend loads at http://15.237.26.46
- ✅ Admin panel accessible at http://15.237.26.46/admin/
- ✅ API endpoints responding at http://15.237.26.46/api/
- ✅ All services running without errors
- ✅ No permission or connection issues

## If Something Goes Wrong
1. Check the logs first
2. Verify all services are running
3. Check file permissions and ownership
4. Ensure all dependencies are installed
5. Verify network configuration
6. Check the troubleshooting section in DEPLOYMENT_GUIDE.md

## 🎉 You're Done!
Your Alex Design portfolio is now live on AWS Lightsail!
