#!/usr/bin/env python3
"""Trigger a test image post for email approval"""
import sys
import os
sys.path.insert(0, '/app')

from main import app, planner_queue, post_to_blotato, video_engine, SETTINGS
import time

with app.app_context():
    # Add test post to queue if empty
    if len(planner_queue) == 0:
        print("[INFO] Adding test image post to queue...")
        planner_queue.append({
            "title": "Career Success Tips",
            "caption": "Transform your career with expert guidance! 🚀\n\n#CareerGrowth #JobSearch #Success",
            "script": "",
            "logo": "Default",
            "type": "post",
            "visual_prompt": "Professional business office, modern career success theme, motivational atmosphere",
            "platform": "instagram",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    print(f"[INFO] Queue has {len(planner_queue)} items")
    
    # Trigger first item
    if planner_queue:
        item = planner_queue.pop(0)
        print(f"[INFO] Triggering: {item['title']}")
        
        # Generate image
        m_path, fname = video_engine.create_image_post(
            item['title'],
            item['caption'],
            visual_prompt=item.get('visual_prompt', ''),
            platform='instagram',
            show_branding=True
        )
        
        if m_path:
            print(f"[SUCCESS] Generated: {fname}")
            
            # Send for approval
            post_data = {
                "title": item['title'],
                "caption": item['caption'],
                "platforms": ["facebook", "instagram", "linkedin", "tiktok", "youtube"],
                "media_url": m_path,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            results = post_to_blotato(post_data)
            print(f"[SUCCESS] Approval emails sent to: virtualjobguru.social@gmail.com")
            print(f"[INFO] Check your email for approval links!")
        else:
            print(f"[ERROR] Generation failed: {fname}")
