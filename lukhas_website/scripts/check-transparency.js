#!/usr/bin/env node
/* Checks that pages under app/(public|auth)/**/page.(tsx|mdx)
   include either <TransparencyBox ...> or data-transparency="present". */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const GLOBS = [
  'app/public', 'app/auth',
  'app/(public)', 'app/(auth)', // support route groups
  'app/login', 'app/signup', 'app/pricing' // also check auth-related pages
];

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p, acc);
    else if (/page\.(tsx|mdx)$/i.test(name)) acc.push(p);
  }
  return acc;
}

const targets = GLOBS.flatMap(g => walk(path.join(ROOT, g)));
const offenders = [];

for (const file of targets) {
  const src = fs.readFileSync(file, 'utf8');
  const hasBox = /<\s*TransparencyBox\b/.test(src) || /data-transparency\s*=\s*["']present["']/.test(src);
  if (!hasBox) offenders.push(file);
}

if (offenders.length) {
  console.error('❌ Missing <TransparencyBox> on:');
  for (const f of offenders) console.error('  -', path.relative(ROOT, f));
  process.exit(1);
} else {
  console.log('✅ Transparency present on all (public|auth) pages.');
}