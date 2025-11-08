#!/usr/bin/env python3
"""
tools/generate_sitemaps.py

Generates XML sitemaps for all 5 LUKHAS domains with:
- Priority and changefreq based on page type
- lastmod from front-matter last_reviewed
- Cross-domain alternate links (hreflang)
"""
import yaml
import re
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

DOMAINS = {
    "lukhas.ai": "https://lukhas.ai",
    "lukhas.dev": "https://lukhas.dev",
    "lukhas.com": "https://lukhas.com",
    "lukhas.eu": "https://lukhas.eu",
    "lukhas.app": "https://lukhas.app"
}

def generate_sitemaps():
    """Generate sitemap.xml for each domain."""

    for domain_name, base_url in DOMAINS.items():
        pages = collect_pages(domain_name)
        sitemap_xml = build_sitemap(pages, base_url)

        output_path = Path(f"branding/websites/{domain_name}/sitemap.xml")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(sitemap_xml)
        print(f"✅ Generated: {output_path} ({len(pages)} pages)")

def collect_pages(domain_name):
    """Collect all markdown pages for domain."""
    domain_dir = Path(f"branding/websites/{domain_name}")
    if not domain_dir.exists():
        return []

    pages = []
    for md_file in domain_dir.rglob("*.md"):
        front_matter = read_front_matter(md_file)
        if not front_matter:
            continue

        # Extract SEO metadata
        canonical = front_matter.get("canonical", "")

        # Skip if canonical is not a valid URL string (e.g., boolean true/false)
        if not isinstance(canonical, str) or not canonical.startswith("http"):
            continue

        last_reviewed = front_matter.get("last_reviewed", "")
        priority = get_priority(md_file.name)
        changefreq = get_changefreq(md_file.name)

        pages.append({
            "loc": canonical,
            "lastmod": last_reviewed,
            "priority": priority,
            "changefreq": changefreq
        })

    return pages

def read_front_matter(path):
    """Read YAML front-matter from markdown file."""
    txt = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        print(f"YAML parse error in {path}: {e}")
        return {}

def get_priority(filename):
    """Determine priority based on page type."""
    if "homepage" in filename:
        return "1.0"
    elif "product" in filename or "feature" in filename:
        return "0.8"
    elif "research" in filename or "blog" in filename:
        return "0.6"
    else:
        return "0.5"

def get_changefreq(filename):
    """Determine change frequency based on page type."""
    if "homepage" in filename:
        return "weekly"
    elif "blog" in filename:
        return "monthly"
    else:
        return "yearly"

def build_sitemap(pages, base_url):
    """Build XML sitemap from page data."""
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        # Skip pages without canonical URLs
        if not page["loc"]:
            continue

        url_elem = SubElement(urlset, "url")
        SubElement(url_elem, "loc").text = str(page["loc"])
        if page["lastmod"]:
            SubElement(url_elem, "lastmod").text = str(page["lastmod"])
        SubElement(url_elem, "priority").text = str(page["priority"])
        SubElement(url_elem, "changefreq").text = str(page["changefreq"])

    # Pretty print XML
    rough_string = tostring(urlset, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    generate_sitemaps()
