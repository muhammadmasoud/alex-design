#!/bin/bash
# optimize-images-simple.sh - Simple image optimization using system tools

echo "🖼️  Simple image optimization using system tools..."

# Install system image optimization tools
echo "📦 Installing system image tools..."
if command -v apt-get >/dev/null 2>&1; then
    # Ubuntu/Debian
    sudo apt-get update >/dev/null 2>&1
    sudo apt-get install -y jpegoptim optipng webp >/dev/null 2>&1
elif command -v yum >/dev/null 2>&1; then
    # RHEL/CentOS
    sudo yum install -y jpegoptim optipng libwebp-tools
elif command -v dnf >/dev/null 2>&1; then
    # Fedora
    sudo dnf install -y jpegoptim optipng libwebp-tools
else
    echo "⚠️  Package manager not found. Please install jpegoptim, optipng, and webp manually."
fi

# Create optimized directories
mkdir -p backend/projects/optimized
mkdir -p backend/projects/webp
mkdir -p backend/projects/originals

echo "🔧 Optimizing existing images..."

# Optimize images in backend/projects
if [ -d "backend/projects" ]; then
    cd backend/projects
    
    # Backup original images
    cp *.{jpg,jpeg,png,gif} originals/ 2>/dev/null || true
    
    echo "🗜️  Compressing JPEG images..."
    for img in *.jpg *.jpeg; do
        if [ -f "$img" ]; then
            jpegoptim --max=80 --strip-all --dest=optimized "$img" 2>/dev/null || cp "$img" optimized/
        fi
    done
    
    echo "🗜️  Compressing PNG images..."
    for img in *.png; do
        if [ -f "$img" ]; then
            optipng -o3 -dir optimized "$img" 2>/dev/null || cp "$img" optimized/
        fi
    done
    
    echo "📱 Converting to WebP..."
    for img in *.jpg *.jpeg *.png; do
        if [ -f "$img" ]; then
            cwebp -q 80 "$img" -o "webp/${img%.*}.webp" 2>/dev/null || echo "⚠️  WebP conversion failed for $img"
        fi
    done
    
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
    if [ "$savings" -gt 0 ]; then
        percent=$((savings * 100 / original_size))
        echo "💾 Space saved: ${percent}% ($((savings / 1024)) MB)"
    else
        echo "💾 Images were already well optimized"
    fi
fi

echo "✅ Image optimization complete!"
echo ""
echo "📋 Manual steps:"
echo "   1. Review optimized images in backend/projects/optimized/"
echo "   2. Replace originals with optimized versions if satisfied:"
echo "      cp backend/projects/optimized/* backend/projects/"
echo "   3. Update your Django settings to serve WebP when supported"
