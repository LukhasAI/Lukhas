#!/usr/bin/env python3
"""
Capture and save DALL-E 3 generated dream images
"""

import asyncio
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

from openai import OpenAI


async def generate_and_save_dream_images():
    """Generate dream images and save them locally"""

    print("\n" + "=" * 80)
    print("🎨 NIAS DREAM IMAGE GENERATION & CAPTURE")
    print("=" * 80 + "\n")

    client = OpenAI()

    # Create directory for dream images
    images_dir = Path("dream_images")
    images_dir.mkdir(exist_ok=True)

    # Define dream scenarios
    dream_prompts = [
        {
            "name": "winter_comfort",
            "prompt": "A dreamlike ethereal scene of a soft cashmere sweater floating in pastel winter clouds, "
            "watercolor style, gentle morning light, peaceful and serene, no text, artistic and poetic",
            "product": "Cashmere Sweater",
        },
        {
            "name": "wellness_journey",
            "prompt": "Abstract dreamscape of organic wellness elements - floating herbs, soft golden light, "
            "zen garden atmosphere, minimalist and calming, watercolor meditation scene, no text",
            "product": "Wellness Bundle",
        },
        {
            "name": "holiday_gift",
            "prompt": "Magical gift box opening with soft light and stardust, dreamy holiday atmosphere, "
            "warm candlelight glow, ethereal and festive, painted in soft pastels, no text",
            "product": "Holiday Gift Set",
        },
        {
            "name": "adventure_calling",
            "prompt": "Surreal landscape where mountains meet clouds, path leading to adventure, "
            "golden hour lighting, dreamlike and inspiring, impressionist painting style, no text",
            "product": "Adventure Package",
        },
    ]

    generated_images = []

    for i, scenario in enumerate(dream_prompts, 1):
        print(f"\n{'─'*60}")
        print(f"Scenario {i}: {scenario['name'].replace('_', ' ').title()}")
        print(f"Product: {scenario['product']}")
        print(f"{'─'*60}")

        print("\n⏳ Generating dream image with DALL-E 3...")
        print(f"Prompt: '{scenario['prompt'][:100]}...'")

        try:
            # Generate image
            response = client.images.generate(
                model="dall-e-3",
                prompt=scenario["prompt"],
                size="1024x1024",
                quality="hd",  # High quality for better dreams
                n=1,
                style="vivid",  # More artistic style
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            print("\n✅ Image generated successfully!")
            print(f"URL: {image_url[:80]}...")

            # Download and save image
            print("\n📥 Downloading image...")
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                # Save with timestamp and scenario name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"dream_{scenario['name']}_{timestamp}.png"
                filepath = images_dir / filename

                with open(filepath, "wb") as f:
                    f.write(image_response.content)

                print(f"💾 Saved as: {filepath}")

                # Store metadata
                metadata = {
                    "filename": filename,
                    "scenario": scenario["name"],
                    "product": scenario["product"],
                    "original_prompt": scenario["prompt"],
                    "revised_prompt": revised_prompt,
                    "url": image_url,
                    "timestamp": timestamp,
                    "path": str(filepath),
                }

                generated_images.append(metadata)

                print("\n📊 Image Details:")
                print("   Size: 1024x1024 pixels")
                print("   Quality: HD")
                print("   Style: Vivid (artistic)")

            else:
                print(f"❌ Failed to download image: {image_response.status_code}")

        except Exception as e:
            print(f"❌ Error generating image: {e}")
            continue

    # Create HTML gallery
    if generated_images:
        print(f"\n\n{'='*80}")
        print("📸 CREATING DREAM GALLERY")
        print("=" * 80)

        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>NIAS Dream Commerce - Generated Dreams</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        .dream-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }
        .dream-image {
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .dream-title {
            font-size: 1.5em;
            margin: 15px 0 10px 0;
            font-weight: 600;
        }
        .dream-product {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .dream-prompt {
            font-size: 0.9em;
            opacity: 0.8;
            line-height: 1.5;
            margin-top: 10px;
            font-style: italic;
        }
        .timestamp {
            font-size: 0.8em;
            opacity: 0.6;
            margin-top: 10px;
        }
        .header-emoji {
            font-size: 1.5em;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="header-emoji">🌙</span>NIAS Dream Commerce Gallery<span class="header-emoji">✨</span></h1>
        <div class="subtitle">AI-Generated Dreams • Not Advertisements, But Poetry</div>
        
        <div class="gallery">
"""

        for img in generated_images:
            dream_title = img["scenario"].replace("_", " ").title()
            html_content += f"""
            <div class="dream-card">
                <img src="{img['filename']}" alt="{dream_title}" class="dream-image">
                <div class="dream-title">{dream_title}</div>
                <div class="dream-product">Product: {img['product']}</div>
                <div class="dream-prompt">{img['original_prompt']}</div>
                <div class="timestamp">Generated: {img['timestamp']}</div>
            </div>
"""

        html_content += """
        </div>
        
        <div style="text-align: center; margin-top: 50px; opacity: 0.8;">
            <p>Generated by NIAS Dream Commerce System with DALL-E 3</p>
            <p style="font-style: italic;">"Not selling, but dreaming together."</p>
        </div>
    </div>
</body>
</html>
"""

        gallery_path = images_dir / "dream_gallery.html"
        with open(gallery_path, "w") as f:
            f.write(html_content)

        print(f"\n🌐 HTML Gallery created: {gallery_path}")
        print(f"   Open in browser: file://{gallery_path.absolute()}")

    # Save metadata JSON
    if generated_images:
        import json

        metadata_path = images_dir / "dream_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(generated_images, f, indent=2)
        print(f"\n📄 Metadata saved: {metadata_path}")

    print(f"\n\n{'='*80}")
    print("✅ DREAM IMAGE CAPTURE COMPLETE")
    print("=" * 80)
    print(f"\n📁 Images saved in: {images_dir.absolute()}")
    print(f"   • {len(generated_images)} dream images generated")
    print("   • HTML gallery created")
    print("   • Metadata JSON saved")

    print("\n🎨 The NIAS system has successfully:")
    print("   • Generated ethereal dream imagery (not product photos)")
    print("   • Created poetic visual experiences")
    print("   • Saved dreams for offline viewing")
    print("   • Built a beautiful gallery showcase")

    return generated_images


if __name__ == "__main__":
    print("🚀 Starting NIAS Dream Image Capture...")
    results = asyncio.run(generate_and_save_dream_images())

    if results:
        print(f"\n💫 Success! Generated {len(results)} dream images")
        print("\n🌟 These aren't ads - they're visual poems about products")
        print("   Each one crafted to inspire, not to sell")
    else:
        print("\n⚠️ No images were generated. Check the errors above.")
