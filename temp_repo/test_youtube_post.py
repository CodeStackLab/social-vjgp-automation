#!/usr/bin/env python3
"""Test YouTube posting with real token"""
import sys
import os
sys.path.insert(0, '/app')

from main import app, planner_queue, post_to_blotato, video_engine, SETTINGS, SOCIAL_TOKENS
import time

with app.app_context():
    # Check YouTube token
    youtube_token = SOCIAL_TOKENS.get('youtube', {})
    print(f"[INFO] YouTube Token Status: {youtube_token.get('status')}")
    print(f"[INFO] Token Length: {len(youtube_token.get('access_token', ''))}")
    print(f"[INFO] Connected At: {youtube_token.get('connected_at')}")
    
    # Add test video post to queue
    print("\n[INFO] Adding test video post for YouTube...")
    planner_queue.append({
        "title": "Career Success Tips",
        "caption": "Transform your career with expert guidance! 🚀 #CareerGrowth #JobSearch",
        "script": "Your career success starts here. Expert guidance for job seekers.",
        "logo": "Default",
        "type": "reel",
        "visual_prompt": "Professional business office, modern career coaching session",
        "platform": "youtube",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    print(f"[INFO] Queue has {len(planner_queue)} items")
    
    # Trigger the post
    if planner_queue:
        item = planner_queue.pop(0)
        print(f"\n[INFO] Triggering: {item['title']}")
        print(f"[INFO] Type: {item.get('type', 'reel')}")
        
        # Generate video
        print("[INFO] Generating video...")
        m_path, fname = video_engine.create_branded_video(
            item['script'],
            visual_prompt=item.get('visual_prompt', ''),
            model_name=SETTINGS['api_config'].get('video_model', 'veo-3.1-fast-generate-001'),
            api_key=SETTINGS['api_config'].get('vertex_api_key'),
            project_id=SETTINGS['api_config'].get('vertex_project_id')
        )
        
        if m_path:
            print(f"[SUCCESS] Video generated: {fname}")
            print(f"[INFO] Video path: {m_path}")
            
            # Create post data for YouTube only
            post_data = {
                "title": item['title'],
                "caption": item['caption'],
                "platforms": ["youtube"],  # Only YouTube
                "media_url": m_path,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Post directly (SMTP disabled for this test)
            print("\n[INFO] Posting to YouTube...")
            results = post_to_blotato(post_data)
            
            if results:
                print(f"\n[SUCCESS] YouTube posting result:")
                print(f"Results: {results}")
            else:
                print(f"\n[ERROR] Posting failed")
        else:
            print(f"[ERROR] Video generation failed: {fname}")
    else:
        print("[ERROR] Queue is empty")
