
import os
import sys
import time

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import video_engine

def generate_final_hr_batch():
    print("🚀 Generating Final HR Professional Batch...")
    
    test_cases = [
        {
            "platform": "instagram",
            "title": "Mastering the Interview",
            "caption": "Body language matters more than you think.",
            "visual_prompt": "professional job interview between a recruiter and candidate"
        },
        {
            "platform": "tiktok",
            "title": "Team Collaboration",
            "caption": "The secret to a high-performing culture.",
            "visual_prompt": "corporate team brainstorming in a modern glass office"
        },
        {
            "platform": "instagram",
            "title": "Top HR Strategies",
            "caption": "How to retain your best talent in 2026.",
            "visual_prompt": "HR manager reviewing resumes on a clean modern desk"
        }
    ]
    
    for i, data in enumerate(test_cases):
        print(f"\n📸 Case {i+1}: {data['title']}")
        path, filename = video_engine.create_image_post(
            data['title'], 
            data['caption'], 
            style='hero', 
            platform=data['platform'],
            visual_prompt=data['visual_prompt']
        )
        if path:
            print(f"✅ Success: {filename}")
        else:
            print(f"❌ Failed: {data['title']}")

if __name__ == "__main__":
    generate_final_hr_batch()
