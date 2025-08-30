@echo off
echo 🔄 Switching Image Optimizer to Production Mode...

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

REM Update config to production mode
powershell -Command "(Get-Content 'portfolio\image_optimizer_config.py') -replace 'PRODUCTION_MODE = False', 'PRODUCTION_MODE = True' | Set-Content 'portfolio\image_optimizer_config.py'"

echo ✅ Production mode enabled
echo ✅ WebP Lossless: True
echo ✅ WebP Quality: 100
echo ✅ JPEG Quality: 100

echo.
echo 🎯 Image Optimizer is now in PRODUCTION MODE
echo    - 0%% quality loss
echo    - Lossless WebP encoding
echo    - Maximum quality preservation
echo    - Slower processing (expected for production)
echo.
echo 📁 Configuration file: portfolio\image_optimizer_config.py
echo 🔄 To switch back to development mode, run: switch_to_development.bat
echo.
echo 🚀 Ready for production deployment!
pause
