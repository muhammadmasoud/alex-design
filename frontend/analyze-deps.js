import fs from 'fs';
import path from 'path';

// Read package.json
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const dependencies = Object.keys(packageJson.dependencies);

// Recursively find all .tsx and .ts files
function findFiles(dir, files = []) {
  const dirFiles = fs.readdirSync(dir);
  for (const file of dirFiles) {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory() && !filePath.includes('node_modules')) {
      findFiles(filePath, files);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      files.push(filePath);
    }
  }
  return files;
}

// Find all imports in source files
const sourceFiles = findFiles('./src');
const usedDependencies = new Set();

sourceFiles.forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  dependencies.forEach(dep => {
    if (content.includes(`from "${dep}"`) || content.includes(`from '${dep}'`) || 
        content.includes(`import "${dep}"`) || content.includes(`import '${dep}'`)) {
      usedDependencies.add(dep);
    }
  });
});

// Find potentially unused dependencies
const unusedDeps = dependencies.filter(dep => !usedDependencies.has(dep));

console.log('🔍 Dependency Analysis Results:');
console.log('================================');
console.log(`📦 Total dependencies: ${dependencies.length}`);
console.log(`✅ Used dependencies: ${usedDependencies.size}`);
console.log(`❌ Potentially unused: ${unusedDeps.length}`);

if (unusedDeps.length > 0) {
  console.log('\n🚨 Potentially unused dependencies:');
  unusedDeps.forEach(dep => console.log(`  - ${dep}`));
  console.log('\n💡 Review these dependencies and consider removing if truly unused.');
}

// Find heavy Radix UI components
const radixDeps = dependencies.filter(dep => dep.startsWith('@radix-ui/'));
console.log(`\n🎨 Radix UI components: ${radixDeps.length}`);
radixDeps.forEach(dep => {
  const isUsed = usedDependencies.has(dep);
  console.log(`  ${isUsed ? '✅' : '❌'} ${dep}`);
});
