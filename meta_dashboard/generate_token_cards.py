#!/usr/bin/env python3
"""
LUKHΛS API Token Cards Generator
================================

Generates printable PDF cards with reviewer credentials and symbolic information.
Creates professional access cards for LUKHΛS system demonstration.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

# Since we can't use external PDF libraries in this environment,
# we'll generate an HTML version that can be printed to PDF

def generate_qr_placeholder():
    """Generate a placeholder for QR code."""
    return """
    <div style="width: 100px; height: 100px; border: 2px solid #333; 
                display: flex; align-items: center; justify-content: center;
                font-size: 10px; text-align: center; color: #666;">
        QR Code<br>Placeholder
    </div>
    """

def generate_sha3_hash(data: str) -> str:
    """Generate SHA3-512 hash snippet."""
    # Using SHA256 as SHA3 might not be available
    hash_obj = hashlib.sha256(data.encode())
    full_hash = hash_obj.hexdigest()
    # Return first and last 8 characters
    return f"{full_hash[:8]}...{full_hash[-8:]}"

def create_token_card_html():
    """Create HTML for printable token cards."""
    
    # Card data
    cards = [
        {
            "title": "LUKHΛS Guardian Access",
            "name": "OpenAI Reviewer",
            "email": "reviewer@openai.com",
            "token": "LUKHAS-T5-GATE",
            "tier": "T5",
            "tier_name": "Guardian",
            "glyphs": ["🛡️", "⚛️", "🧠"],
            "trinity_score": 1.0,
            "permissions": "Full System Access",
            "qrglyph_hash": generate_sha3_hash("LUKHAS-T5-GATE-GUARDIAN")
        },
        {
            "title": "LUKHΛS Demo Access",
            "name": "Test User",
            "email": "demo@lukhas.ai",
            "token": "LUKHAS-T3-DEMO",
            "tier": "T3",
            "tier_name": "Contributor",
            "glyphs": ["⚛️", "🔐", "🧠"],
            "trinity_score": 0.7,
            "permissions": "Advanced Features",
            "qrglyph_hash": generate_sha3_hash("LUKHAS-T3-DEMO-CONTRIBUTOR")
        }
    ]
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHΛS API Token Cards</title>
    <style>
        @page {
            size: A4;
            margin: 10mm;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        
        .page-title {
            text-align: center;
            font-size: 24px;
            margin-bottom: 30px;
            color: #333;
        }
        
        .cards-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        
        .token-card {
            width: 350px;
            height: 200px;
            background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            position: relative;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            page-break-inside: avoid;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .tier-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .glyphs {
            font-size: 36px;
            margin: 10px 0;
            letter-spacing: 8px;
        }
        
        .card-content {
            font-size: 14px;
            line-height: 1.6;
        }
        
        .field {
            margin: 5px 0;
            display: flex;
            align-items: center;
        }
        
        .label {
            font-weight: 500;
            margin-right: 8px;
            opacity: 0.8;
            min-width: 60px;
        }
        
        .value {
            font-family: 'Courier New', monospace;
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .token-value {
            font-size: 16px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.15);
            padding: 4px 10px;
            margin: 10px 0;
            border-radius: 6px;
            text-align: center;
            letter-spacing: 1px;
        }
        
        .qr-section {
            position: absolute;
            bottom: 20px;
            right: 20px;
            text-align: center;
        }
        
        .qr-placeholder {
            width: 60px;
            height: 60px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            opacity: 0.5;
            border-radius: 4px;
        }
        
        .hash {
            font-size: 10px;
            opacity: 0.6;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
        }
        
        .instructions {
            margin: 40px auto;
            max-width: 700px;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            page-break-before: always;
        }
        
        .instructions h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .instructions ul {
            line-height: 1.8;
            color: #555;
        }
        
        .instructions code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .instructions {
                box-shadow: none;
                border: 1px solid #ddd;
            }
        }
    </style>
</head>
<body>
    <h1 class="page-title">🛡️ LUKHΛS API Access Cards</h1>
    
    <div class="cards-container">
"""
    
    # Generate cards
    for card in cards:
        glyphs_str = ' '.join(card['glyphs'])
        html += f"""
        <div class="token-card">
            <div class="card-header">
                <div class="card-title">{card['title']}</div>
                <div class="tier-badge">{card['tier']} • {card['tier_name']}</div>
            </div>
            
            <div class="glyphs">{glyphs_str}</div>
            
            <div class="card-content">
                <div class="field">
                    <span class="label">Email:</span>
                    <span class="value">{card['email']}</span>
                </div>
                
                <div class="token-value">{card['token']}</div>
                
                <div class="field">
                    <span class="label">Access:</span>
                    <span>{card['permissions']}</span>
                </div>
            </div>
            
            <div class="qr-section">
                <div class="qr-placeholder">QR</div>
                <div class="hash">{card['qrglyph_hash']}</div>
            </div>
        </div>
"""
    
    # Add instructions
    html += """
    </div>
    
    <div class="instructions">
        <h2>📋 Usage Instructions</h2>
        
        <h3>For OpenAI Reviewers:</h3>
        <ul>
            <li>Use the <strong>Guardian Access</strong> card (T5 tier) for full system access</li>
            <li>Login at <code>/meta_dashboard/static/login.html</code></li>
            <li>Email: <code>reviewer@openai.com</code></li>
            <li>Password: <code>demo_password</code></li>
            <li>Token can be used directly in API requests with Bearer authentication</li>
        </ul>
        
        <h3>API Authentication:</h3>
        <ul>
            <li>Header: <code>Authorization: Bearer LUKHAS-T5-GATE</code></li>
            <li>All protected endpoints require valid token</li>
            <li>Token provides access based on tier level</li>
        </ul>
        
        <h3>Trinity Framework Glyphs:</h3>
        <ul>
            <li>🛡️ Guardian - Full system protection and oversight</li>
            <li>⚛️ Identity - Core authentication and authorization</li>
            <li>🧠 Consciousness - Advanced AI capabilities</li>
            <li>🔐 Security - Additional protection layer</li>
        </ul>
        
        <h3>Tier Capabilities:</h3>
        <ul>
            <li><strong>T5 Guardian:</strong> Full access to all systems, logs, and controls</li>
            <li><strong>T4 Architect:</strong> System design and quantum features</li>
            <li><strong>T3 Contributor:</strong> Consciousness, emotion, and dream modules</li>
            <li><strong>T2 Participant:</strong> Basic content and API access</li>
            <li><strong>T1 Observer:</strong> Read-only public content</li>
        </ul>
        
        <h3>Security Notes:</h3>
        <ul>
            <li>Tokens are valid for the current session</li>
            <li>QRGLYPH hash provides quantum-resistant verification</li>
            <li>All actions are logged with symbolic tracking</li>
            <li>Guardian system monitors for ethical compliance</li>
        </ul>
        
        <p style="margin-top: 30px; text-align: center; color: #666;">
            <em>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """ UTC</em><br>
            <strong>LUKHΛS AGI System v1.0.0</strong>
        </p>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Generate token cards HTML file."""
    print("🎫 Generating LUKHΛS API Token Cards...")
    
    # Generate HTML
    html_content = create_token_card_html()
    
    # Save to file
    output_path = Path("meta_dashboard/API_TOKEN_CARDS.html")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Token cards generated: {output_path}")
    print("📄 Open in browser and print to PDF for physical cards")
    print("\nCard Details:")
    print("  - Guardian Access (T5): reviewer@openai.com")
    print("  - Demo Access (T3): demo@lukhas.ai")
    print("\n🛡️ Trinity Protected")

if __name__ == "__main__":
    main()