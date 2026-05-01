#!/usr/bin/env python3
"""
Veo 3 Fast - Final working version with proper async polling
"""

import sys
import os
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'

import time
from google import genai
from google.genai import types

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"
LOCATION = "us-central1"

prompt = "A professional working confidently in a modern office with natural sunlight, typing on laptop, cinematic quality, vertical 9:16 format"

print("="*70)
print("🎬 VEO 3 FAST - FINAL VERSION")
print("="*70)
print(f"Model: {MODEL}")
print(f"Prompt: {prompt[:60]}...")
print("="*70)
print()

try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    print("✅ Client initialized\n")
    
    print("📤 Starting video generation...")
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio='9:16',
            number_of_videos=1,
            duration_seconds=8
        )
    )
    
    print(f"✅ Operation: {operation.name}\n")
    print("⏳ Polling for completion...\n")
    
    start_time = time.time()
    check_count = 0
    
    # Poll until done
    while operation.done is None or operation.done is False:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        print(f"Check #{check_count}: {elapsed}s elapsed, done={operation.done}, result={type(operation.result)}")
        
        # Timeout after 3 minutes
        if elapsed > 180:
            print(f"\n❌ Timeout after {elapsed}s")
            sys.exit(1)
        
        time.sleep(10)
        
        # Re-check the operation (genai SDK updates properties automatically)
        # Just accessing the property triggers a check
        _ = operation.done
    
    elapsed = int(time.time() - start_time)
    print(f"\n✅ Generation complete! (took {elapsed}s)\n")
    
    # Access result
    if operation.result and hasattr(operation.result, 'generated_videos'):
        videos = operation.result.generated_videos
        
        if videos:
            video_bytes = videos[0].video.data
            
            output_path = "/app/generated_media/videos/veo3_success.mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            
            file_size = len(video_bytes) / (1024 * 1024)
            
            print("="*70)
            print("✅ SUCCESS!")
            print("="*70)
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:.2f} MB")
            print(f"⏱️  Time: {elapsed}s")
            print(f"🌐 URL: https://vjgu.online/videos/videos/veo3_success.mp4")
            print("="*70)
        else:
            print("❌ No videos in result")
    else:
        print(f"❌ Invalid result: {operation.result}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
