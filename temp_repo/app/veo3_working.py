#!/usr/bin/env python3
"""
Veo 3 Fast - Correct polling using wait()
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

prompt = "A professional working in a modern office, typing on laptop, natural lighting, cinematic, vertical 9:16"

print("="*70)
print("🎬 VEO 3 FAST - CORRECT POLLING")
print("="*70)
print(f"Model: {MODEL}")
print("="*70)
print()

try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    print("✅ Client initialized\n")
    
    print("📤 Creating video generation operation...")
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio='9:16',
            number_of_videos=1,
            duration_seconds=8
        )
    )
    
    print(f"✅ Operation created: {operation.name}\n")
    print("⏳ Waiting for completion (typically 20-60 seconds)...\n")
    
    start_time = time.time()
    
    # Use wait() method with timeout
    try:
        # Wait for operation to complete (timeout after 3 minutes)
        operation.wait(timeout=180)
        
        elapsed = int(time.time() - start_time)
        print(f"\n✅ Operation complete! (took {elapsed}s)\n")
        
    except Exception as wait_error:
        elapsed = int(time.time() - start_time)
        print(f"\n⚠️  Wait error after {elapsed}s: {wait_error}")
        print("Trying to get result anyway...\n")
    
    # Get result
    result = operation.result()
    
    if result.generated_videos:
        video_bytes = result.generated_videos[0].video.data
        
        output_path = "/app/generated_media/videos/veo3_fast_working.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes) / (1024 * 1024)
        
        print("="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:.2f} MB")
        print(f"🌐 URL: https://vjgu.online/videos/videos/veo3_fast_working.mp4")
        print("="*70)
    else:
        print("❌ No video in response")
        print(f"Result: {result}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
