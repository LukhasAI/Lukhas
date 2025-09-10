#!/usr/bin/env python3
"""Minimal Photon renderer: emits a simple HTML preview for a Photon JSON.

Usage: python3 tools/render_photon_minimal.py examples/photon_users.json > /tmp/preview.html
"""
import json
import sys


def render(photon):
    title = photon.get("title", "Photon Preview")
    nodes = photon.get("nodes", [])
    html = ['<html><head><meta charset="utf-8"><title>', title, "</title></head><body>"]
    html.append(f"<h1>{title}</h1>")
    html.append("<div style='display:flex;gap:40px;'>")
    for n in nodes:
        html.append("<div style='border:1px solid #ccc;padding:8px;'>")
        html.append(f"<h3>{n.get('label', '')}</h3>")
        html.append(f"<div><strong>kind:</strong> {n.get('kind')}</div>")
        props = n.get("properties", {})
        html.append("<div><em>properties</em><ul>")
        for k, v in props.items():
            html.append(f"<li>{k}: {v}</li>")
        html.append("</ul></div>")
        html.append("</div>")
    html.append("</div>")
    html.append("</body></html>")
    return "\n".join(html)


def main():
    if len(sys.argv) < 2:
        print("Usage: render_photon_minimal.py <photon.json>")
        sys.exit(2)
    p = sys.argv[1]
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    print(render(data))


if __name__ == "__main__":
    main()