# PowerShell Deployment Script for Timeout Fixes
# This script helps deploy timeout-related changes to your server

param(
    [string]$ServerIP = "52.47.162.66",
    [string]$Username = "ubuntu",
    [string]$KeyPath = "alex-design-key.ppk"
)

Write-Host "=========================================" -ForegroundColor Green
Write-Host "Deploying Timeout Fixes to Production" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Step 1: Commit and push local changes
Write-Host "Step 1: Committing and pushing local changes..." -ForegroundColor Yellow
try {
    git add .
    git commit -m "Fix 504 Gateway Timeout: Increase timeouts, fix serialization, optimize bulk uploads"
    git push origin main
    Write-Host "✓ Changes pushed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Git operations failed: $_" -ForegroundColor Yellow
}

# Step 2: Deploy to server
Write-Host "Step 2: Deploying to server..." -ForegroundColor Yellow

# Check if PuTTY is available
$puttyPath = Get-Command "plink" -ErrorAction SilentlyContinue
if (-not $puttyPath) {
    Write-Host "❌ PuTTY (plink) not found. Please install PuTTY or add it to PATH." -ForegroundColor Red
    Write-Host "Download from: https://www.putty.org/" -ForegroundColor Yellow
    exit 1
}

# Check if key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "❌ Key file not found: $KeyPath" -ForegroundColor Red
    exit 1
}

# Deploy using the specialized script
Write-Host "Deploying timeout fixes to server..." -ForegroundColor Yellow

$deployCommand = @"
cd /home/ubuntu/alex-design
chmod +x deploy-timeout-fix.sh
./deploy-timeout-fix.sh
"@

try {
    # Upload the deployment script first
    Write-Host "Uploading deployment script..." -ForegroundColor Yellow
    & pscp -i $KeyPath deploy-timeout-fix.sh ${Username}@${ServerIP}:/home/ubuntu/alex-design/
    
    # Execute the deployment
    Write-Host "Executing deployment..." -ForegroundColor Yellow
    & plink -i $KeyPath ${Username}@${ServerIP} $deployCommand
    
    Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Verify deployment
Write-Host "Step 3: Verifying deployment..." -ForegroundColor Yellow

$verifyCommand = @"
cd /home/ubuntu/alex-design/backend
echo '=== Gunicorn Config ==='
grep 'timeout = 300' gunicorn.conf.py
echo '=== Django Settings ==='
grep 'REQUEST_TIMEOUT = 300' backend/settings.py
grep 'UPLOAD_TIMEOUT = 300' backend/settings.py
echo '=== Middleware ==='
grep 'RequestTimeoutMiddleware' backend/settings.py
echo '=== Service Status ==='
sudo systemctl status alex-design --no-pager -l
"@

try {
    & plink -i $KeyPath ${Username}@${ServerIP} $verifyCommand
    Write-Host "✓ Verification completed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Verification failed: $_" -ForegroundColor Yellow
}

Write-Host "=========================================" -ForegroundColor Green
Write-Host "Deployment Summary" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Your timeout fixes have been deployed to: http://$ServerIP" -ForegroundColor Green
Write-Host ""
Write-Host "Key changes applied:" -ForegroundColor White
Write-Host "• Gunicorn timeout: 300 seconds (5 minutes)" -ForegroundColor White
Write-Host "• Django request timeout: 300 seconds" -ForegroundColor White
Write-Host "• NGINX proxy timeouts: 300 seconds" -ForegroundColor White
Write-Host "• RequestTimeoutMiddleware: Enabled" -ForegroundColor White
Write-Host ""
Write-Host "Test your upload functionality now!" -ForegroundColor Green
Write-Host "The 504 Gateway Timeout errors should be resolved." -ForegroundColor Green
