# Database Migration Guide - Step by Step

## Overview
This guide covers migrating database data from your local machine or another server to your current production server.

## Prerequisites
- ✅ Current server working (fix the `DB_USER=alex_designs` first!)
- 🔍 Identify your data source (local machine or another server)
- 📦 Access to both source and target databases

---

## Method 1: From Local Machine to Server

### Step 1: Backup Current Production Database (Safety First!)
```bash
# On your production server
cd /home/ubuntu/alex-design/backend

# Create backup of current data
pg_dump -U alex_designs -h localhost alex_designs > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -la *.sql
```

### Step 2: Export Data from Local Machine
```bash
# On your local machine (Windows)
cd D:\ITI\alex-design\backend

# Export your local database
pg_dump -U postgres -h 127.0.0.1 alex_designs > local_data_export.sql

# Verify export file size
dir local_data_export.sql
```

### Step 3: Transfer Data to Server
```bash
# Option A: Using SCP (if you have SSH key)
scp local_data_export.sql ubuntu@52.47.162.66:/home/ubuntu/alex-design/backend/

# Option B: Upload via your preferred method (FileZilla, etc.)
# Upload local_data_export.sql to /home/ubuntu/alex-design/backend/
```

### Step 4: Prepare Target Database on Server
```bash
# On your production server
cd /home/ubuntu/alex-design/backend

# Stop Django service to avoid conflicts
sudo systemctl stop alex-design

# Clear existing data (CAREFUL!)
psql -U alex_designs -h localhost alex_designs -c "
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END \$\$;
"
```

### Step 5: Import Data
```bash
# Import the data
psql -U alex_designs -h localhost alex_designs < local_data_export.sql

# Check if import was successful
psql -U alex_designs -h localhost alex_designs -c "\dt"  # List tables
psql -U alex_designs -h localhost alex_designs -c "SELECT COUNT(*) FROM auth_user;"  # Check user count
```

### Step 6: Fix Permissions and Ownership
```bash
# Ensure alex_designs user owns everything
psql -U postgres -h localhost alex_designs -c "
REASSIGN OWNED BY postgres TO alex_designs;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO alex_designs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO alex_designs;
"
```

### Step 7: Restart and Test
```bash
# Start Django service
sudo systemctl start alex-design

# Check service status
sudo systemctl status alex-design

# Test admin panel
curl -I https://52.47.162.66/admin/
```

---

## Method 2: From Another Server to Current Server

### Step 1: Export from Source Server
```bash
# SSH to source server
ssh username@source-server-ip

# Export database
pg_dump -U source_user -h localhost source_database > source_data_export.sql

# Compress for faster transfer
gzip source_data_export.sql
```

### Step 2: Transfer Between Servers
```bash
# Option A: Direct transfer (if servers can communicate)
scp source_data_export.sql.gz ubuntu@52.47.162.66:/home/ubuntu/alex-design/backend/

# Option B: Download to local, then upload
# Download from source → Upload to target
```

### Step 3: Decompress and Import
```bash
# On target server
cd /home/ubuntu/alex-design/backend
gunzip source_data_export.sql.gz

# Follow steps 4-7 from Method 1
```

---

## Method 3: Using Django Management Commands (Recommended for Django Data)

### Step 1: Export Data as JSON (Source)
```bash
# On source machine/server
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > full_data_export.json

# Or export specific apps
python manage.py dumpdata portfolio > portfolio_data.json
python manage.py dumpdata auth.User > users_data.json
```

### Step 2: Transfer JSON Files
```bash
# Transfer to target server
scp *.json ubuntu@52.47.162.66:/home/ubuntu/alex-design/backend/
```

### Step 3: Import Data (Target)
```bash
# On target server
cd /home/ubuntu/alex-design/backend

# Stop service
sudo systemctl stop alex-design

# Run migrations to ensure schema is ready
python manage.py migrate

# Import data
python manage.py loaddata full_data_export.json

# Or import specific data
python manage.py loaddata users_data.json
python manage.py loaddata portfolio_data.json

# Start service
sudo systemctl start alex-design
```

---

## Troubleshooting

### If Import Fails:
```bash
# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Check Django logs
sudo journalctl -u alex-design -f

# Restore backup if needed
psql -U alex_designs -h localhost alex_designs < backup_before_migration_*.sql
```

### Common Issues:
1. **Permission denied**: Run `GRANT ALL PRIVILEGES` commands
2. **User conflicts**: May need to reset user passwords after import
3. **Sequence issues**: Reset sequences after import:
   ```sql
   SELECT setval(pg_get_serial_sequence('table_name', 'id'), MAX(id)) FROM table_name;
   ```

### Verify Migration Success:
```bash
# Check key tables
psql -U alex_designs -h localhost alex_designs -c "
SELECT 'Users: ' || COUNT(*) FROM auth_user;
SELECT 'Projects: ' || COUNT(*) FROM portfolio_project;
SELECT 'Services: ' || COUNT(*) FROM portfolio_service;
"

# Test admin login
python manage.py createsuperuser  # If needed
```

---

## Final Checklist
- [ ] ✅ Current database backed up
- [ ] ✅ Data exported from source
- [ ] ✅ Data transferred to target
- [ ] ✅ Database cleared (if full replacement)
- [ ] ✅ Data imported successfully
- [ ] ✅ Permissions corrected
- [ ] ✅ Django service restarted
- [ ] ✅ Admin panel accessible
- [ ] ✅ Website functionality tested

**Choose the method that best fits your data source and comfort level!**
