#!/bin/bash
# deploy-optimizations.sh - Deploy performance optimizations on Ubuntu server

echo "🚀 Deploying performance optimizations..."

# Make sure we're in the right directory
if [ ! -f "package.json" ] && [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Not in project root directory"
    exit 1
fi

# Navigate to frontend if we're in project root
if [ -f "frontend/package.json" ]; then
    cd frontend
fi

echo "📦 Installing dependencies..."
npm install

echo "🔧 Installing performance tools..."
npm install --save-dev rollup-plugin-visualizer vite-bundle-analyzer

echo "📝 Updating package.json with performance scripts..."
# Add performance scripts to package.json if they don't exist
if ! grep -q "analyze" package.json; then
    # Create a temporary file with the new scripts
    node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));

// Add performance scripts
pkg.scripts = pkg.scripts || {};
Object.assign(pkg.scripts, {
    'analyze': 'npm run build && npx rollup-plugin-visualizer dist/stats.html --open',
    'size-check': 'npm run build && npx vite-bundle-analyzer',
    'perf:check': 'npm run build && echo \"Build size:\" && du -sh dist/'
});

// Add basic size monitoring comment
pkg.bundleTargets = {
    'vendor': '< 200KB',
    'main': '< 100KB',
    'total': '< 5MB'
};

fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
console.log('✅ Performance scripts added to package.json');
"
fi

echo "🏗️  Building optimized production bundle..."
npm run build

echo "📊 Analyzing bundle size..."
npm run perf:check

echo "🧹 Running cleanup..."
cd .. 2>/dev/null || true
chmod +x cleanup.sh
./cleanup.sh

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Check bundle analysis: open frontend/dist/stats.html"
echo "   2. Monitor performance: npm run size-check"
echo "   3. Regular cleanup: ./cleanup.sh"
