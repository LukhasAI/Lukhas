#!/usr/bin/env node
/**
 * Validate that each entry in branding/site.sections.json maps to an existing Next.js route.
 * - Fails for missing routes on status:"public"
 * - Warns (non-blocking) for status:"candidate"
 *
 * Supported app roots (auto-detected if they exist):
 *   - lukhas_website/app
 *   - apps/web/app
 *   - apps/site/app
 *   - apps/website/app
 *
 * Route discovery:
 *   - Recursively finds page files with extensions tsx|jsx|mdx|ts|js
 *   - Builds a normalized route per file by removing group folders
 *   - Compares normalized route to each section.slug
 */

import fs from "node:fs";
import path from "node:path";

const SITE_SECTIONS_PATH = "branding/site.sections.json";
if (!fs.existsSync(SITE_SECTIONS_PATH)) {
  console.error(`❌ Missing ${SITE_SECTIONS_PATH}`);
  process.exit(1);
}

const sections = JSON.parse(fs.readFileSync(SITE_SECTIONS_PATH, "utf8")).sections || [];
const appRoots = ["lukhas_website/app", "apps/web/app", "apps/site/app", "apps/website/app"].filter(p => fs.existsSync(p));
if (appRoots.length === 0) {
  console.error("❌ No Next.js app roots found (checked lukhas_website/app, apps/web/app, apps/site/app, apps/website/app).");
  process.exit(1);
}

const PAGE_EXT = /\.(tsx|jsx|mdx|ts|js)$/i;
const pageFiles = [];

// Walk filesystem
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p);
    else if (PAGE_EXT.test(p) && path.basename(p).startsWith("page.")) pageFiles.push(p);
  }
}

// Normalize a page file path to a route (removing (group) segments)
function routeFromPageFile(appRoot, filePath) {
  let rel = path.relative(appRoot, path.dirname(filePath)); // e.g., "" or "privacy" or "(marketing)/privacy"
  const segs = rel.split(path.sep).filter(Boolean).filter(s => !(s.startsWith("(") && s.endsWith(")")));
  const route = "/" + segs.join("/");
  return route === "/" ? "/" : route.replace(/\/+/g, "/");
}

// Build set of existing routes across all app roots
const existingRoutes = new Set();
for (const root of appRoots) {
  walk(root);
  for (const file of pageFiles) {
    if (!file.startsWith(root)) continue;
    existingRoutes.add(routeFromPageFile(root, file));
  }
}

// Validate sections
let hardErrors = 0;
let warnings = 0;

function isPublic(section) {
  // default to public if status missing
  return (section.status || "public") === "public";
}

for (const s of sections) {
  const slug = (s.slug || "").trim();
  if (!slug || !slug.startsWith("/")) {
    console.error(`❌ Invalid or missing slug for section:${s.key}`);
    hardErrors++;
    continue;
  }

  const exists = existingRoutes.has(slug);
  if (exists) {
    console.log(`✅ ${slug} → route found`);
    continue;
  }

  if (isPublic(s)) {
    console.error(`❌ Missing route for PUBLIC section:${s.key} (${slug})`);
    hardErrors++;
  } else {
    console.warn(`⚠️  Candidate section without route yet: ${s.key} (${slug})`);
    warnings++;
  }
}

// Summary + exit
if (hardErrors > 0) {
  console.error(`\n❌ Site sections check failed: ${hardErrors} missing public routes${warnings ? `, ${warnings} warnings` : ""}.`);
  process.exit(1);
} else {
  console.log(`\n✅ Site sections OK (${warnings} warnings).`);
  process.exit(0);
}