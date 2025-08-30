#!/bin/bash

# Switch Image Optimizer to Production Mode
# This script sets the image optimizer to use lossless compression for maximum quality

echo "🔄 Switching Image Optimizer to Production Mode..."

# Check if config file exists
if [ ! -f "portfolio/image_optimizer_config.py" ]; then
    echo "❌ Configuration file not found!"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Backup current config
cp portfolio/image_optimizer_config.py portfolio/image_optimizer_config.py.backup
echo "✅ Backup created: portfolio/image_optimizer_config.py.backup"

# Update config to production mode
sed -i 's/PRODUCTION_MODE = False/PRODUCTION_MODE = True/g' portfolio/image_optimizer_config.py
sed -i 's/PRODUCTION_MODE = False/PRODUCTION_MODE = True/g' portfolio/image_optimizer_config.py

echo "✅ Production mode enabled"
echo "✅ WebP Lossless: True"
echo "✅ WebP Quality: 100"
echo "✅ JPEG Quality: 100"

echo ""
echo "🎯 Image Optimizer is now in PRODUCTION MODE"
echo "   - 0% quality loss"
echo "   - Lossless WebP encoding"
echo "   - Maximum quality preservation"
echo "   - Slower processing (expected for production)"
echo ""
echo "📁 Configuration file: portfolio/image_optimizer_config.py"
echo "🔄 To switch back to development mode, run: ./switch_to_development.sh"
echo ""
echo "🚀 Ready for production deployment!"
