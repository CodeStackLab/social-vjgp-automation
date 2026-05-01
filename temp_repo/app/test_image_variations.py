
import os
import sys
import time
from platform_optimizer import PLATFORM_SPECS

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import video_engine

def test_variations():
    print("🚀 Starting Comprehensive Image Generation Test...")
    
    test_data = [
        {
            "platform": "instagram",
            "style": "hero",
            "title": "5 Tips for Remote Work",
            "caption": "Working from home can be productive if you follow these simple hacks."
        },
        {
            "platform": "linkedin",
            "style": "list",
            "title": "Interview Checklist",
            "caption": "- Dress professionally\n- Research the company\n- Prepare 3 questions\n- Body language matters\n- Bring extra resumes"
        },
        {
            "platform": "facebook",
            "style": "table",
            "title": "Career Myths vs Reality",
            "caption": "Passion leads to money | Skill leads to value\nSuccess is overnight | Success takes consistency\nHR is your enemy | HR is your partner"
        },
        {
            "platform": "tiktok",
            "style": "hero",
            "title": "Salary Negotiation",
            "caption": "Don't settle for less than you're worth. Use these scripts."
        }
    ]
    
    for i, data in enumerate(test_data):
        print(f"\n📸 Testing Case {i+1}: {data['platform']} ({data['style']})")
        try:
            path, filename = video_engine.create_image_post(
                data['title'], 
                data['caption'], 
                style=data['style'], 
                platform=data['platform']
            )
            
            if path and os.path.exists(path):
                from PIL import Image
                img = Image.open(path)
                w, h = img.size
                spec = PLATFORM_SPECS[data['platform']]
                
                print(f"✅ SUCCESS: {filename}")
                print(f"📐 Dimensions: {w}x{h} (Expected {spec['width']}x{spec['height']})")
            else:
                print(f"❌ FAILED: Generation returned {path}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_variations()
