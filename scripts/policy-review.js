import fs from 'node:fs'; 
import path from 'node:path';

console.log('🔍 Scanning for claims requiring human review...\n');

// These words often indicate claims that need verification
const claimsToReview = /\b(revolutionary|guaranteed|flawless|perfect|zero-?risk|unbreakable|unlimited|breakthrough|cutting-?edge|world-?class|industry-?leading|state-?of-?the-?art|unparalleled|game-?changing)\b/i;

// Focus on public-facing content
const publicPaths = [
  'branding',
  'lukhas_website/app',
  'docs',
  'README.md'
];

const flaggedItems = [];

function scanFile(filePath) {
  if(!fs.existsSync(filePath)) return;
  
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  
  lines.forEach((line, idx) => {
    const match = line.match(claimsToReview);
    if(match) {
      flaggedItems.push({
        file: filePath,
        line: idx + 1,
        claim: match[0],
        context: line.trim().substring(0, 100)
      });
    }
  });
}

function scanDir(dirPath) {
  if(!fs.existsSync(dirPath)) return;
  
  const items = fs.readdirSync(dirPath);
  for(const item of items) {
    const fullPath = path.join(dirPath, item);
    
    // Skip build artifacts and dependencies
    if(/(node_modules|\.next|\.git|build|dist)/.test(fullPath)) continue;
    
    const stat = fs.statSync(fullPath);
    if(stat.isDirectory()) {
      scanDir(fullPath);
    } else if(/\.(md|mdx|tsx?|jsx?|html)$/.test(fullPath)) {
      scanFile(fullPath);
    }
  }
}

// Scan all public paths
publicPaths.forEach(p => {
  if(fs.existsSync(p)) {
    const stat = fs.statSync(p);
    if(stat.isDirectory()) {
      scanDir(p);
    } else {
      scanFile(p);
    }
  }
});

// Report findings
if(flaggedItems.length > 0) {
  console.log(`📋 Found ${flaggedItems.length} claims requiring human review:\n`);
  
  // Group by file for easier review
  const byFile = {};
  flaggedItems.forEach(item => {
    if(!byFile[item.file]) byFile[item.file] = [];
    byFile[item.file].push(item);
  });
  
  Object.entries(byFile).forEach(([file, items]) => {
    console.log(`\n📄 ${file}:`);
    items.forEach(item => {
      console.log(`   Line ${item.line}: "${item.claim}" - Review needed`);
      console.log(`   Context: ${item.context}`);
    });
  });
  
  console.log('\n💡 Review Process:');
  console.log('   1. Check if claim is factually accurate');
  console.log('   2. Verify with evidence/metrics if quantitative');
  console.log('   3. Consider replacing with specific, verifiable language');
  console.log('   4. If keeping, document justification in BDR');
  
  // Write review file for tracking
  const reviewFile = {
    timestamp: new Date().toISOString(),
    totalFlags: flaggedItems.length,
    items: flaggedItems,
    status: 'pending_review'
  };
  
  fs.writeFileSync('branding/claims-review.json', JSON.stringify(reviewFile, null, 2));
  console.log('\n📝 Review list saved to: branding/claims-review.json');
  
  // Don't fail CI, just warn
  console.log('\n⚠️  Claims flagged for review - not blocking');
  process.exit(0);
} else {
  console.log('✅ No unverified claims found in public content');
}