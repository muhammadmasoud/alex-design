#!/bin/bash
# optimize-images.sh - Optimize images on Ubuntu server

echo "🖼️  Setting up image optimization..."

# Check if running as root or with sudo access
if [ "$EUID" -eq 0 ]; then
    # Running as root
    echo "📦 Installing image optimization tools globally..."
    npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant imagemin-gifsicle
else
    # Try to install globally with sudo, fallback to local if no sudo
    echo "📦 Installing image optimization tools..."
    if sudo -n true 2>/dev/null; then
        echo "Installing globally with sudo..."
        sudo npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant imagemin-gifsicle
    else
        echo "No sudo access. Installing locally in project..."
        cd frontend 2>/dev/null || { echo "Creating temp npm project for tools..."; mkdir -p .image-tools && cd .image-tools; }
        npm init -y >/dev/null 2>&1
        npm install imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant imagemin-gifsicle
        # Add node_modules/.bin to PATH for this session
        export PATH="$PWD/node_modules/.bin:$PATH"
        cd - >/dev/null
    fi
fi

# Create optimized directories
mkdir -p backend/media/optimized
mkdir -p backend/media/webp
mkdir -p backend/projects/optimized
mkdir -p backend/projects/webp

echo "🔧 Optimizing existing images..."

# Optimize images in backend/projects
if [ -d "backend/projects" ]; then
    cd backend/projects
    
    # Backup original images
    mkdir -p originals
    cp *.{jpg,jpeg,png,gif} originals/ 2>/dev/null || true
    
    echo "🗜️  Compressing PNG images..."
    if command -v imagemin >/dev/null 2>&1; then
        imagemin *.png --out-dir=optimized --plugin=pngquant --plugin.pngquant.quality=0.6-0.8 2>/dev/null || true
    else
        echo "⚠️  imagemin not found, skipping PNG optimization"
    fi
    
    echo "🗜️  Compressing JPEG images..."
    if command -v imagemin >/dev/null 2>&1; then
        imagemin *.{jpg,jpeg} --out-dir=optimized --plugin=mozjpeg --plugin.mozjpeg.quality=80 2>/dev/null || true
    else
        echo "⚠️  imagemin not found, skipping JPEG optimization"
    fi
    
    echo "📱 Converting to WebP..."
    if command -v imagemin >/dev/null 2>&1; then
        imagemin *.{jpg,jpeg,png} --out-dir=webp --plugin=webp --plugin.webp.quality=80 2>/dev/null || true
    else
        echo "⚠️  imagemin not found, skipping WebP conversion"
    fi
    
    cd ../..
fi

# Optimize images in backend/media
if [ -d "backend/media" ]; then
    cd backend/media
    
    find . -name "*.png" -exec imagemin {} --out-dir=optimized --plugin=pngquant \; 2>/dev/null || true
    find . -name "*.jpg" -exec imagemin {} --out-dir=optimized --plugin=mozjpeg \; 2>/dev/null || true
    find . -name "*.jpeg" -exec imagemin {} --out-dir=optimized --plugin=mozjpeg \; 2>/dev/null || true
    
    cd ../..
fi

echo "📊 Image optimization results:"
echo "Original images: $(find backend/projects/originals -type f 2>/dev/null | wc -l) files"
echo "Optimized images: $(find backend/projects/optimized -type f 2>/dev/null | wc -l) files"
echo "WebP images: $(find backend/projects/webp -type f 2>/dev/null | wc -l) files"

# Calculate space savings
original_size=$(du -s backend/projects/originals 2>/dev/null | cut -f1 || echo "0")
optimized_size=$(du -s backend/projects/optimized 2>/dev/null | cut -f1 || echo "0")

if [ "$original_size" -gt 0 ] && [ "$optimized_size" -gt 0 ]; then
    savings=$((original_size - optimized_size))
    percent=$((savings * 100 / original_size))
    echo "💾 Space saved: ${percent}% ($((savings / 1024)) MB)"
fi

echo "✅ Image optimization complete!"
echo ""
echo "📋 Manual steps:"
echo "   1. Review optimized images in backend/projects/optimized/"
echo "   2. Replace originals with optimized versions if satisfied"
echo "   3. Update your Django settings to serve WebP when supported"
