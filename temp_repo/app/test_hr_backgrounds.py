
import os
import sys
import time

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import video_engine

def test_hr_steering():
    print("🚀 Testing HR Background Steering...")
    
    test_data = [
        {
            "platform": "instagram",
            "style": "hero",
            "title": "Interview Success",
            "caption": "How to impress your recruiter.",
            "visual_prompt": "Beautiful scenery" # Should be steered to HR
        },
        {
            "platform": "tiktok",
            "style": "hero",
            "title": "Team Building",
            "caption": "Building a strong culture.",
            "visual_prompt": "Office team collaborating" # Already has keywords
        }
    ]
    
    for i, data in enumerate(test_data):
        print(f"\n📸 Case {i+1}: {data['visual_prompt']}")
        path, filename = video_engine.create_image_post(
            data['title'], 
            data['caption'], 
            style=data['style'], 
            platform=data['platform'],
            visual_prompt=data['visual_prompt']
        )
        if path:
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Failed Case {i+1}")

if __name__ == "__main__":
    test_hr_steering()
