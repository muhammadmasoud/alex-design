# cleanup.ps1 - Windows PowerShell cleanup script

Write-Host "🧹 Starting project cleanup..." -ForegroundColor Green

# Remove Python cache files
Write-Host "🔍 Removing Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Include "*__pycache__*" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove duplicate images
Write-Host "🖼️  Checking for duplicate images..." -ForegroundColor Yellow
$projectsPath = "backend\projects"
if (Test-Path $projectsPath) {
    # Remove specific duplicates we found
    $duplicates = @(
        "about2_mpZ3fXv.PNG",
        "about2_PxAk9rF.PNG", 
        "about2_QFHFQdI.PNG",
        "about2_TcCmb4Z.PNG",
        "about2_YlYu1am.PNG"
    )
    
    foreach ($file in $duplicates) {
        $fullPath = Join-Path $projectsPath $file
        if (Test-Path $fullPath) {
            Remove-Item $fullPath -Force
            Write-Host "✅ Removed: $file" -ForegroundColor Green
        }
    }
    
    # Find other potential duplicates by size
    Write-Host "🔍 Checking for other duplicates by file size..." -ForegroundColor Yellow
    $imageFiles = Get-ChildItem -Path $projectsPath -Include "*.jpg","*.png","*.jpeg" -File
    $duplicates = $imageFiles | Group-Object Length | Where-Object Count -gt 1
    
    foreach ($group in $duplicates) {
        Write-Host "⚠️  Files with same size ($($group.Name) bytes):" -ForegroundColor Yellow
        $group.Group | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }
    }
}

# Clean build artifacts
Write-Host "🏗️  Cleaning build artifacts..." -ForegroundColor Yellow
Remove-Item -Path "frontend\dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "frontend\.vite" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup finished successfully!" -ForegroundColor Green
Write-Host "💾 Total project size:" -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { "$([math]::Round($_.Sum / 1MB, 2)) MB" }
