# Update Database User in Production Server

## Overview
You need to change the database user from `a7aa` to `alex_designs` on your production server.

## Steps to Execute on Your Production Server

### 1. Connect to Your Production Server
```bash
ssh ubuntu@your-server-ip
# or however you normally connect to your server
```

### 2. Navigate to Your Project Directory
```bash
cd /home/ubuntu/alex-design/backend
```

### 3. Update the .env File on Production
```bash
# Backup current .env file
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update DB_USER in .env file
sed -i 's/DB_USER=a7aa/DB_USER=alex_designs/' .env

# Verify the change
grep "DB_USER" .env
```

### 4. Create New PostgreSQL User
```bash
# Connect to PostgreSQL as postgres user
sudo -u postgres psql

# Inside PostgreSQL prompt, run these commands:
CREATE USER alex_designs WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE alex_designs TO alex_designs;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO alex_designs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO alex_designs;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO alex_designs;

# Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alex_designs;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alex_designs;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO alex_designs;

# Exit PostgreSQL
\q
```

### 5. Test Database Connection
```bash
# Test the new user can connect
psql -U alex_designs -d alex_designs -h localhost -W

# If successful, you should see the PostgreSQL prompt
# Type \q to exit
```

### 6. Test Django Database Connection
```bash
# Test Django can connect with new user
python manage.py dbshell

# If successful, you'll see the PostgreSQL prompt
# Type \q to exit
```

### 7. Restart Your Django Application
```bash
# Restart your Django service (adjust service name if different)
sudo systemctl restart alex-design

# Check service status
sudo systemctl status alex-design

# Check logs to ensure no database errors
sudo journalctl -u alex-design -f --lines=50
```

### 8. Optional: Remove Old User (After Confirming Everything Works)
```bash
# Only do this after confirming the new user works perfectly
sudo -u postgres psql
DROP USER a7aa;
\q
```

## Troubleshooting

### If Database Connection Fails:
1. Check that the new user was created:
   ```bash
   sudo -u postgres psql -c "\du"
   ```

2. Verify database permissions:
   ```bash
   sudo -u postgres psql -d alex_designs -c "\z"
   ```

3. Check Django logs:
   ```bash
   sudo journalctl -u alex-design -f
   ```

### If Service Won't Start:
1. Check configuration syntax:
   ```bash
   python manage.py check
   ```

2. Test database connection manually:
   ```bash
   python manage.py dbshell
   ```

## Summary of Changes
- ✅ Local .env updated: `DB_USER=alex_designs`
- 🔄 Production .env needs update
- 🔄 PostgreSQL user needs to be created
- 🔄 Django service needs restart
- 🔄 Testing required

## Current Local Configuration
```env
DB_USER=alex_designs  # ✅ Updated locally
```

**Next Step:** Execute these commands on your production server in the order listed above.
