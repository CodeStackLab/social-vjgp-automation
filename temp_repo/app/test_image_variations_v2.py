
import os
import sys
import time
from platform_optimizer import PLATFORM_SPECS

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import video_engine

def test_new_variations():
    print("🚀 Starting New Image Generation Test (Layouts + Branding Toggle)...")
    
    test_data = [
        {
            "platform": "instagram",
            "style": "hero",
            "title": "Unlocking Your Potential",
            "caption": "Your career is a journey, not a destination. Start today with Virtual Job Guru.",
            "show_branding": True,
            "visual_prompt": "modern office with sunset through large windows, cinematic lighting, 8k"
        },
        {
            "platform": "tiktok",
            "style": "hero",
            "title": "Top 5 Remote Jobs",
            "caption": "1. Data Analyst\n2. Software Engineer\n3. UX Designer\n4. Digital Marketer\n5. Product Manager",
            "show_branding": False,
            "visual_prompt": None
        },
        {
            "platform": "instagram",
            "style": "hero",
            "title": "Confidence is Key",
            "caption": "Believe in yourself and the world will follow. Join our webinar.",
            "show_branding": False,
            "visual_prompt": "abstract motivational background, vibrant colors"
        }
    ]
    
    for i, data in enumerate(test_data):
        print(f"\n📸 Testing Case {i+1}: {data['platform']} ({'Branded' if data['show_branding'] else 'Clean'})")
        try:
            path, filename = video_engine.create_image_post(
                data['title'], 
                data['caption'], 
                style=data['style'], 
                platform=data['platform'],
                show_branding=data['show_branding'],
                visual_prompt=data['visual_prompt']
            )
            
            if path and os.path.exists(path):
                from PIL import Image
                img = Image.open(path)
                w, h = img.size
                spec = PLATFORM_SPECS[data['platform']]
                
                print(f"✅ SUCCESS: {filename}")
                print(f"📐 Dimensions: {w}x{h} (Expected {spec['width']}x{spec['height']})")
                print(f"🔗 Path: {path}")
            else:
                print(f"❌ FAILED: Generation returned {path}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_new_variations()
