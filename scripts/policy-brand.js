import fs from 'node:fs'; 
import path from 'node:path';

console.log('Scanning brand compliance (focused check)...');

// Focus on key files only to avoid noise
const keyFiles = [
  'branding/MATRIZ_BRAND_GUIDE.md',
  'branding/PRESS_KIT_README.md',
  'lukhas_website/app/matriz/page.tsx',
  'lukhas_website/app/page.tsx'
];

const bannedWords = /\b(revolutionary|guaranteed|flawless|perfect|zero-?risk|unbreakable|unlimited)\b/i;
let violations = 0;

for(const file of keyFiles) {
  if(fs.existsSync(file)) {
    const content = fs.readFileSync(file, 'utf8');
    const match = content.match(bannedWords);
    if(match) {
      console.error(`❌ Banned word "${match[0]}" in ${file}`);
      violations++;
    }
  }
}

if(violations > 0) {
  console.error(`\n💡 Found ${violations} brand violations. Replace with factual descriptions.`);
  process.exit(1);
} else {
  console.log('✅ Key files brand compliant');
}