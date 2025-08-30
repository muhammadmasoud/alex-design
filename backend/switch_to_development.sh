#!/bin/bash

# Switch Image Optimizer to Development Mode
# This script sets the image optimizer to use high-quality compression for faster processing

echo "🔄 Switching Image Optimizer to Development Mode..."

# Check if config file exists
if [ ! -f "portfolio/image_optimizer_config.py" ]; then
    echo "❌ Configuration file not found!"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Backup current config
cp portfolio/image_optimizer_config.py portfolio/image_optimizer_config.py.backup
echo "✅ Backup created: portfolio/image_optimizer_config.py.backup"

# Update config to development mode
sed -i 's/PRODUCTION_MODE = True/PRODUCTION_MODE = False/g' portfolio/image_optimizer_config.py

echo "✅ Development mode enabled"
echo "✅ WebP Lossless: False"
echo "✅ WebP Quality: 85"
echo "✅ JPEG Quality: 88"

echo ""
echo "🔧 Image Optimizer is now in DEVELOPMENT MODE"
echo "   - High quality (minimal loss)"
echo "   - Faster processing"
echo "   - Smaller file sizes"
echo "   - Ideal for development and testing"
echo ""
echo "📁 Configuration file: portfolio/image_optimizer_config.py"
echo "🔄 To switch back to production mode, run: ./switch_to_production.sh"
echo ""
echo "⚡ Ready for development!"
