# Production Email Setup Guide for Ubuntu Server

## 🚨 Critical: Your email is failing because the Ubuntu server lacks proper email configuration

### Step 1: Create Gmail App Password

1. **Go to your Gmail account settings**
2. **Enable 2-Factor Authentication** (required for App Passwords)
3. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it: "Alex Design Website"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 2: Create Production .env File on Ubuntu Server

SSH into your Ubuntu server and create the `.env` file:

```bash
# SSH into your server
ssh ubuntu@52.47.162.66

# Navigate to your backend directory
cd /home/ubuntu/alex-design/backend

# Create the .env file
nano .env
```

**Add this content to your .env file:**

```env
# Django Production Environment Variables
SECRET_KEY=your-super-secret-key-here-generate-new-one
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
EMAIL_HOST_USER=mohamedaboelhamd765@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password-here
DEFAULT_FROM_EMAIL=noreply@alexdesign.com
CONTACT_EMAIL=mohamedaboelhamd765@gmail.com

# Production Settings
ALLOWED_HOSTS=52.47.162.66,2a05:d012:18a:1600:539:6792:3ed7:c389

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
```

### Step 3: Test Email Configuration

```bash
# Test the email configuration
cd /home/ubuntu/alex-design/backend
python manage.py test_email --to mohamedaboelhamd765@gmail.com
```

### Step 4: Restart Your Application

```bash
# Restart the Django application
sudo systemctl restart alex-design
sudo systemctl restart nginx

# Check status
sudo systemctl status alex-design
```

### Step 5: Verify Email Logs

Check the application logs to see email status:

```bash
# Check Django logs
sudo journalctl -u alex-design -f

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 🔧 Common Issues & Solutions

### Issue 1: "Authentication failed"
- **Solution**: Use Gmail App Password, not regular password
- **Check**: 2FA must be enabled on Gmail account

### Issue 2: "Connection refused"
- **Solution**: Check if port 587 is open
- **Test**: `telnet smtp.gmail.com 587`

### Issue 3: "Environment variables not found"
- **Solution**: Ensure .env file is in correct location: `/home/ubuntu/alex-design/backend/.env`
- **Check**: File permissions: `chmod 600 .env`

### Issue 4: Email sent but not received
- **Check**: Gmail spam folder
- **Check**: Correct recipient email in CONTACT_EMAIL

## 📧 Email Flow Explanation

1. **User submits contact form** → Frontend sends to Django API
2. **Django validates data** → ContactSerializer processes form
3. **Email sent via Gmail SMTP** → Using your credentials
4. **Success/Failure handled** → User sees appropriate message

## 🚀 Quick Fix Commands

Run these on your Ubuntu server:

```bash
# 1. Navigate to backend
cd /home/ubuntu/alex-design/backend

# 2. Create .env with your email credentials
cat > .env << 'EOF'
EMAIL_HOST_USER=mohamedaboelhamd765@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=noreply@alexdesign.com
CONTACT_EMAIL=mohamedaboelhamd765@gmail.com
DJANGO_ENV=production
PRODUCTION=true
DEBUG=False
EOF

# 3. Test email
python manage.py test_email --to mohamedaboelhamd765@gmail.com

# 4. Restart services
sudo systemctl restart alex-design
```

## ✅ Verification Checklist

- [ ] Gmail App Password created
- [ ] .env file created on Ubuntu server
- [ ] Email test command successful
- [ ] Django service restarted
- [ ] Contact form test successful
- [ ] Email received in inbox

---
**Note**: Replace `your-app-password-here` with your actual Gmail App Password!
