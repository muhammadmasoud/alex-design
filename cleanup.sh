#!/bin/bash
# cleanup.sh - Cross-platform cleanup script for Ubuntu server

echo "🧹 Starting project cleanup..."

# Remove Python cache files
echo "🔍 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove duplicate images (check for duplicates by size and name pattern)
echo "🖼️  Checking for duplicate images..."
cd backend/projects 2>/dev/null || { echo "No backend/projects directory found"; }

# Find duplicate images by size and similar names
if [ -d "." ]; then
    # Remove specific duplicates we found (about2_*.PNG files)
    rm -f about2_mpZ3fXv.PNG about2_PxAk9rF.PNG about2_QFHFQdI.PNG about2_TcCmb4Z.PNG about2_YlYu1am.PNG 2>/dev/null || true
    echo "✅ Removed duplicate about2_*.PNG files"
    
    # General duplicate finder (optional - checks for files with same size)
    echo "🔍 Checking for other duplicates by file size..."
    find . -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) -exec ls -la {} \; | \
    awk '{print $5, $9}' | sort | uniq -d -f 1 | \
    while read size file; do
        echo "⚠️  Potential duplicate found: $file (size: $size bytes)"
    done
fi

cd - >/dev/null

# Clean build artifacts
echo "🏗️  Cleaning build artifacts..."
rm -rf frontend/dist 2>/dev/null || true
rm -rf frontend/.vite 2>/dev/null || true

# Calculate space saved
echo "📊 Cleanup complete!"
echo "💾 Run this to check total size: du -sh ."

echo "✅ Cleanup finished successfully!"
