#!/usr/bin/env python3
"""
tools/svg_validator.py

SVG Validator for LUKHAS Branding Assets

Validates SVG files against design token constraints:
- viewBox presence and minimum dimensions
- No embedded raster images
- Stroke width within recommended ranges
- Contrast ratios meet WCAG 2 AA (≥4.5:1)
- Color usage against theme palette

Usage:
  python3 tools/svg_validator.py --svg path/to/icon.svg --tokens branding/tokens/lukhas-tokens.json --theme dark

Exit Codes:
  0 - All checks passed
  2 - Validation issues found

Author: LUKHAS AI (generated)
Version: 1.0
Date: 2025-11-06
"""

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def hex_to_rgb(hexc):
    """Convert hex color to RGB tuple (0-1 range)"""
    hexc = hexc.strip()
    if hexc.startswith('#'):
        hexc = hexc[1:]
    if len(hexc) == 3:
        hexc = ''.join([c * 2 for c in hexc])
    r = int(hexc[0:2], 16) / 255.0
    g = int(hexc[2:4], 16) / 255.0
    b = int(hexc[4:6], 16) / 255.0
    return (r, g, b)


def lum(r, g, b):
    """Calculate relative luminance per WCAG 2.0"""
    def channel(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(hex1, hex2):
    """Calculate contrast ratio between two hex colors"""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    L1 = lum(r1, g1, b1)
    L2 = lum(r2, g2, b2)
    if L1 < L2:
        L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)


def get_theme_bg(tokens, theme):
    """Extract background color from theme tokens"""
    theme_data = tokens.get('theme', {}).get(theme)
    if not theme_data:
        raise ValueError(f"Theme {theme} not found in tokens.")
    return theme_data.get('bg')


def parse_svg(svg_path):
    """Parse SVG file and return root element"""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    return root


def attr(elem, name, default=None):
    """Get element attribute with default"""
    return elem.get(name) if elem.get(name) is not None else default


def hex_from_style(style_str, prop):
    """Extract hex color from style string like 'fill:#fff;stroke:#000'"""
    if not style_str:
        return None
    parts = style_str.split(';')
    for p in parts:
        if ':' in p:
            k, v = p.split(':', 1)
            if k.strip() == prop:
                return v.strip()
    return None


def normalize_color(col):
    """Normalize color to hex format"""
    if not col or col.lower() in ('none', 'currentcolor'):
        return None

    if col.startswith('#'):
        return col

    # Try rgb(r,g,b) format
    m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', col)
    if m:
        r, g, b = map(int, m.groups())
        return '#%02x%02x%02x' % (r, g, b)

    return None


def validate_svg(svg_path, tokens, theme, args):
    """
    Validate SVG against design constraints.
    Returns list of issues (empty if valid).
    """
    issues = []

    try:
        root = parse_svg(svg_path)
    except Exception as e:
        issues.append(f"Failed to parse SVG: {e}")
        return issues

    try:
        bg = get_theme_bg(tokens, theme)
    except Exception as e:
        issues.append(f"Failed to get theme background: {e}")
        return issues

    # Check 1: viewBox presence
    vb = root.get('viewBox')
    if not vb:
        issues.append("Missing viewBox attribute.")
    else:
        try:
            parts = list(map(float, vb.strip().split()))
            if len(parts) != 4:
                issues.append(f"Invalid viewBox format: {vb}")
            else:
                vw = parts[2]
                vh = parts[3]
                if vw < args.minsize or vh < args.minsize:
                    issues.append(
                        f"viewBox dimensions {vw}x{vh} < min recommended {args.minsize}px."
                    )
        except Exception as e:
            issues.append(f"Failed to parse viewBox: {e}")

    # Check 2: No embedded raster images
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    images = root.findall('.//{http://www.w3.org/2000/svg}image')
    if images:
        issues.append(
            "SVG contains raster <image> elements; avoid embedding raster images."
        )

    # Check 3: Stroke widths and contrast ratios
    shape_tags = ['path', 'circle', 'rect', 'ellipse', 'line', 'polyline', 'polygon']

    for tag in shape_tags:
        for el in root.findall(f'.//{{{ns["svg"]}}}{tag}'):
            # Check stroke-width
            sw = el.get('stroke-width')
            style = el.get('style')

            if sw is None and style:
                sw = hex_from_style(style, 'stroke-width')

            if sw is not None:
                try:
                    # Strip 'px' suffix if present
                    sw_match = re.match(r'([\d.]+)', str(sw))
                    if sw_match:
                        swv = float(sw_match.group(1))
                        if swv < args.stroke_min or swv > args.stroke_max:
                            issues.append(
                                f"Element <{tag}> stroke-width={swv} outside recommended "
                                f"[{args.stroke_min}, {args.stroke_max}]."
                            )
                except Exception as e:
                    issues.append(f"Failed to parse stroke-width '{sw}': {e}")

            # Check fill/stroke contrast
            fill = el.get('fill')
            stroke = el.get('stroke')

            # Check style attribute
            if style:
                if not fill:
                    fill = hex_from_style(style, 'fill')
                if not stroke:
                    stroke = hex_from_style(style, 'stroke')

            # Evaluate contrast for each color type
            for ctype, col in [('fill', fill), ('stroke', stroke)]:
                hexcol = normalize_color(col)
                if hexcol:
                    try:
                        cr = contrast_ratio(hexcol, bg)
                        if cr < 4.5:
                            issues.append(
                                f"<{tag}> {ctype} color {hexcol} has contrast {cr:.2f} "
                                f"vs background {bg} < 4.5 (WCAG 2 AA minimum)."
                            )
                    except Exception as e:
                        issues.append(
                            f"Color contrast check error for {hexcol}: {e}"
                        )

    # Check 4: Color palette usage
    palette = []
    th = tokens.get('theme', {}).get(theme) or {}
    for k, v in th.items():
        if k in ('bg', 'surface', 'matriz', 'identity', 'dev', 'enterprise',
                 'success', 'warning', 'danger', 'text'):
            if v:
                palette.append(v.upper())

    # Collect all fill colors
    fills = set()
    for el in root.findall(f'.//{{{ns["svg"]}}}*'):
        f = el.get('fill')
        style = el.get('style')

        if style and not f:
            f = hex_from_style(style, 'fill')

        hexcol = normalize_color(f)
        if hexcol:
            fills.add(hexcol.upper())

    # Warn about colors not in palette
    for f in fills:
        if f not in palette:
            issues.append(
                f"Fill color {f} not found in theme palette for '{theme}' (warning)."
            )

    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate SVG files against LUKHAS design token constraints"
    )
    parser.add_argument('--svg', required=True, help='Path to SVG file')
    parser.add_argument('--tokens', required=True, help='Path to design tokens JSON')
    parser.add_argument(
        '--theme',
        choices=['dark', 'light', 'assistive'],
        default='dark',
        help='Theme to validate against (default: dark)'
    )
    parser.add_argument(
        '--minsize',
        type=int,
        default=24,
        help='Minimum recommended icon dimension in pixels (default: 24)'
    )
    parser.add_argument(
        '--stroke-min',
        type=float,
        default=0.6,
        help='Minimum stroke width for 24px grid (default: 0.6)'
    )
    parser.add_argument(
        '--stroke-max',
        type=float,
        default=4.0,
        help='Maximum stroke width for 24px grid (default: 4.0)'
    )

    args = parser.parse_args()

    # Validate paths
    svg_path = Path(args.svg)
    if not svg_path.exists():
        print(f"Error: SVG file not found: {svg_path}", file=sys.stderr)
        sys.exit(2)

    tokens_path = Path(args.tokens)
    if not tokens_path.exists():
        print(f"Error: Tokens file not found: {tokens_path}", file=sys.stderr)
        sys.exit(2)

    # Load tokens
    try:
        tokens = json.loads(tokens_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error: Failed to parse tokens JSON: {e}", file=sys.stderr)
        sys.exit(2)

    # Run validation
    issues = validate_svg(svg_path, tokens, args.theme, args)

    # Output results
    if issues:
        print(f"❌ SVG Validation Issues ({len(issues)}):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\nFile: {svg_path}")
        print(f"Theme: {args.theme}")
        sys.exit(2)
    else:
        print("✅ SVG Validation passed.")
        print(f"   File: {svg_path}")
        print(f"   Theme: {args.theme}")
        sys.exit(0)


if __name__ == "__main__":
    main()
