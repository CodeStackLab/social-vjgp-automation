
import os
import sys
import requests
import json
import time
import subprocess

# Add current directory to path
sys.path.append(os.getcwd())
import social_uploader
from video_utils import convert_to_9_16

def generate_test_video():
    """Generates a 5-second test video"""
    output_path = "/app/generated_media/temp/final_test_video.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate 16:9 video that needs resizing
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'testsrc=duration=5:size=1920x1080:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def test_integration():
    print("[INFO] Starting Final Integration Test...")
    
    # 1. Generate Video
    video_path = generate_test_video()
    print(f"[INFO] Generated test video: {video_path}")
    
    # 2. Test Resizing
    success, resized_path = convert_to_9_16(video_path)
    if success:
        print(f"[SUCCESS] Video Resizing: {resized_path}")
    else:
        print(f"[ERROR] Video Resizing Failed: {resized_path}")
        return

    # 3. Load Credentials
    with open('/app/data/app_settings.json', 'r') as f:
        settings = json.load(f)
        
    tokens = settings.get('social_tokens', {})
    
    # 4. Test LinkedIn
    if 'linkedin' in tokens:
        print("\n[TESTING] LinkedIn...")
        try:
            li_token = tokens['linkedin']['access_token']
            # Using the resized video URL (simulated local path for now as verify script runs inside docker)
            # LinkedIn needs a public URL for media normally, but we are testing the logic. 
            # Wait, social_uploader.post_to_linkedin takes a URL.
            # We can't easily test media upload without a public URL pointing to this container.
            # So we will test TEXT post for LinkedIn to verify auth, 
            # and rely on previous duplicate check for media path.
            
            resp = social_uploader.post_to_linkedin(li_token, f"Final Integration Test {time.time()}", None)
            print(f"[LINKEDIN] Result: {resp}")
        except Exception as e:
            print(f"[LINKEDIN] Error: {e}")
    else:
        print("[LINKEDIN] No token found.")

    # 5. Test TikTok
    if 'tiktok' in tokens:
        print("\n[TESTING] TikTok...")
        try:
            tk_token = tokens['tiktok']['access_token']
            open_id = tokens['tiktok'].get('open_id', 'me')
            
            # TikTok upload requires LOCAL file path, which we have (resized_path)
            resp = social_uploader.post_to_tiktok(tk_token, open_id, resized_path, "Final Test #AI")
            print(f"[TIKTOK] Result: {resp}")
        except Exception as e:
            print(f"[TIKTOK] Error: {e}")
    else:
        print("[TIKTOK] No token found.")

if __name__ == "__main__":
    test_integration()
