#!/usr/bin/env python3
"""
Veo 3 Fast - CORRECT Implementation from Official Documentation
Uses client.operations.get() for proper polling
"""

import sys
import os
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

import time
from google import genai
from google.genai.types import GenerateVideosConfig

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"

prompt = "A professional working confidently in a modern office with natural sunlight, typing on laptop, cinematic quality, vertical 9:16 format"

print("="*70)
print("🎬 VEO 3 FAST - OFFICIAL DOCUMENTATION METHOD")
print("="*70)
print(f"Model: {MODEL}")
print(f"Project: {PROJECT_ID}")
print("="*70)
print()

try:
    # Initialize client
    client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')
    print("✅ Client initialized\n")
    
    print("📤 Starting video generation...")
    
    # Generate video - NO output_gcs_uri means video bytes returned in response
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=GenerateVideosConfig(
            aspect_ratio='9:16',
            # No output_gcs_uri - we want bytes in response
        ),
    )
    
    print(f"✅ Operation created: {operation.name}\n")
    print("⏳ Polling with client.operations.get()...\n")
    
    start_time = time.time()
    check_count = 0
    
    # CORRECT POLLING METHOD from documentation
    while not operation.done:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        print(f"Check #{check_count}: {elapsed}s elapsed, done={operation.done}")
        
        # Timeout after 3 minutes
        if elapsed > 180:
            print(f"\n❌ Timeout after {elapsed}s")
            sys.exit(1)
        
        time.sleep(15)  # Documentation uses 15 seconds
        
        # CRITICAL: Refresh operation status using client.operations.get()
        operation = client.operations.get(operation)
    
    elapsed = int(time.time() - start_time)
    print(f"\n✅ Generation complete! (took {elapsed}s)\n")
    
    # Access result
    if operation.result and hasattr(operation.result, 'generated_videos'):
        videos = operation.result.generated_videos
        
        if videos and len(videos) > 0:
            video_data = videos[0].video
            
            # Check if we have bytes or URI
            if hasattr(video_data, 'video_bytes') and video_data.video_bytes:
                video_bytes = video_data.video_bytes
                
                output_path = "/app/generated_media/videos/veo3_official_method.mp4"
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
                print(f"🌐 URL: https://vjgu.online/videos/videos/veo3_official_method.mp4")
                print("="*70)
            elif hasattr(video_data, 'uri') and video_data.uri:
                print(f"✅ Video stored at GCS: {video_data.uri}")
            else:
                print(f"❌ No video data or URI in response")
        else:
            print("❌ No videos in result")
    else:
        print(f"❌ Invalid result: {operation.result}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
