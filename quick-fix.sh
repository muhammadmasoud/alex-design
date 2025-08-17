#!/bin/bash
# quick-fix.sh - Quick fix for your current Ubuntu situation

echo "🔧 Quick fix for Ubuntu server permissions..."

# Make the simple script executable
chmod +x optimize-images-simple.sh

echo "📦 Installing system image optimization tools..."
sudo apt-get update >/dev/null 2>&1
sudo apt-get install -y jpegoptim optipng webp

echo "🖼️  Running simple image optimization..."
./optimize-images-simple.sh

echo "✅ Quick fix complete!"
echo ""
echo "💡 Your images should now be optimized using system tools instead of npm packages."
