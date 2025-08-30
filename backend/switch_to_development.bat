@echo off
echo 🔄 Switching Image Optimizer to Development Mode...

REM Check if config file exists
if not exist "portfolio\image_optimizer_config.py" (
    echo ❌ Configuration file not found!
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

REM Backup current config
copy "portfolio\image_optimizer_config.py" "portfolio\image_optimizer_config.py.backup"
echo ✅ Backup created: portfolio\image_optimizer_config.py.backup

REM Update config to development mode
powershell -Command "(Get-Content 'portfolio\image_optimizer_config.py') -replace 'PRODUCTION_MODE = True', 'PRODUCTION_MODE = False' | Set-Content 'portfolio\image_optimizer_config.py'"

echo ✅ Development mode enabled
echo ✅ WebP Lossless: False
echo ✅ WebP Quality: 85
echo ✅ JPEG Quality: 88

echo.
echo 🔧 Image Optimizer is now in DEVELOPMENT MODE
echo    - High quality (minimal loss)
echo    - Faster processing
echo    - Smaller file sizes
echo    - Ideal for development and testing
echo.
echo 📁 Configuration file: portfolio\image_optimizer_config.py
echo 🔄 To switch back to production mode, run: switch_to_production.bat
echo.
echo ⚡ Ready for development!
pause
