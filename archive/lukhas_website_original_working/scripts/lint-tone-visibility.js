#!/usr/bin/env node
// Warn if visible strings "Poetic|Technical|Plain" appear in user-visible UI
const fs = require('fs')
const path = require('path')

const ROOT = process.cwd()
const dirs = ['app/(public)', 'app/(auth)', 'app/public', 'app/auth', 'app/pricing', 'app/signup', 'app/login', 'app/experience', 'app/matriz']
const offenders = []

function walk(d, out = []) {
  if (!fs.existsSync(d)) return out
  for (const n of fs.readdirSync(d)) {
    const p = path.join(d, n)
    const st = fs.statSync(p)
    if (st.isDirectory()) walk(p, out)
    else if (/page\.(tsx|mdx|jsx|md)$/i.test(n)) out.push(p)
  }
  return out
}

function isVisibleMatch(src, filename) {
  // Check for visible tone words in text content
  // We want to warn about:
  // - Text content that says "Poetic", "Technical", or "Plain" as tone labels
  // But NOT:
  // - data-tone attributes
  // - Comments
  // - Variable names or function names
  // - Common phrases like "Technical Specifications", "Technical Support", etc.
  
  // Remove comments to avoid false positives
  const withoutComments = src
    .replace(/\/\*[\s\S]*?\*\//g, '') // Remove block comments
    .replace(/\/\/.*$/gm, '') // Remove line comments
  
  // Look for the words in string literals or JSX text content
  // This is a simple heuristic - check if the words appear in quoted strings
  // or between JSX tags
  const patterns = [
    // Check for the words in string literals
    /['"`]([^'"`]*\b(Poetic|Technical|Plain)\b[^'"`]*)[`'"]/g,
    // Check for the words in JSX text content (between tags)
    />([^<]*\b(Poetic|Technical|Plain)\b[^<]*)</g,
  ]
  
  for (const pattern of patterns) {
    const matches = withoutComments.matchAll(pattern)
    for (const match of matches) {
      const context = match[0]
      const fullMatch = match[1] || match[0]
      
      // Exclude data-tone, aria-label attributes we're intentionally keeping neutral
      // Also exclude import statements and type definitions
      // And exclude common phrases that aren't tone labels
      if (!context.includes('data-tone') && 
          !context.includes('aria-label') &&
          !context.includes('import') &&
          !context.includes('export type') &&
          !context.includes('type Tier') &&
          !context.includes('// ') &&
          !context.includes('item.poetic') &&
          !context.includes('item.technical') &&
          !context.includes('item.plain') &&
          !context.includes('.poetic') &&
          !context.includes('.technical') &&
          !context.includes('.plain') &&
          // Exclude common non-tone uses of these words
          !fullMatch.includes('Technical Specifications') &&
          !fullMatch.includes('Technical Support') &&
          !fullMatch.includes('Technical Details') &&
          !fullMatch.includes('Technical Documentation') &&
          !fullMatch.includes('Plain Text') &&
          !fullMatch.includes('Plain English')) {
        return true
      }
    }
  }
  
  return false
}

const files = dirs.flatMap(d => walk(path.join(ROOT, d)))

for (const f of files) {
  try {
    const s = fs.readFileSync(f, 'utf8')
    if (isVisibleMatch(s, f)) {
      offenders.push(f)
    }
  } catch (err) {
    console.warn(`Warning: Could not read ${f}: ${err.message}`)
  }
}

if (offenders.length) {
  console.warn('⚠️  Visible tone words detected (avoid showing "Poetic/Technical/Plain" to users):')
  offenders.forEach(f => console.warn(' -', path.relative(ROOT, f)))
  console.warn('\nConsider using neutral labels like "Overview", "Details", "Simple explanation" instead.')
  process.exit(0) // warn-only, don't fail
} else {
  console.log('✅ No visible tone words found in public/auth pages.')
}