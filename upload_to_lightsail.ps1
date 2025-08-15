# PowerShell script to upload Alex Design project to AWS Lightsail
# Make sure you have your SSH key file ready

param(
    [Parameter(Mandatory=$true)]
    [string]$KeyPath,
    
    [Parameter(Mandatory=$true)]
    [string]$InstanceIP = "15.237.26.46"
)

Write-Host "🚀 Starting upload to AWS Lightsail..." -ForegroundColor Green
Write-Host "Instance IP: $InstanceIP" -ForegroundColor Yellow
Write-Host "SSH Key: $KeyPath" -ForegroundColor Yellow

# Check if key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "❌ SSH key file not found: $KeyPath" -ForegroundColor Red
    exit 1
}

# Check if scp is available (requires OpenSSH or Git Bash)
try {
    $scpVersion = scp -V 2>&1
    Write-Host "✅ SCP found: $scpVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ SCP not found. Please install OpenSSH or Git Bash." -ForegroundColor Red
    Write-Host "You can install OpenSSH from Windows Features or use Git Bash." -ForegroundColor Yellow
    exit 1
}

# Create remote directory and upload files
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
ssh -i $KeyPath ubuntu@$InstanceIP "mkdir -p /home/ubuntu/alex-design"

Write-Host "📤 Uploading project files..." -ForegroundColor Yellow
scp -i $KeyPath -r . ubuntu@$InstanceIP:/home/ubuntu/alex-design/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Upload completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Now connect to your instance and run the deployment script:" -ForegroundColor Yellow
    Write-Host "ssh -i `"$KeyPath`" ubuntu@$InstanceIP" -ForegroundColor Cyan
    Write-Host "cd /home/ubuntu/alex-design" -ForegroundColor Cyan
    Write-Host "chmod +x deploy.sh" -ForegroundColor Cyan
    Write-Host "./deploy.sh" -ForegroundColor Cyan
} else {
    Write-Host "❌ Upload failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
