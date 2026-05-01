#!/usr/bin/env python3
"""
Simple Veo 3 Video Generator - NO BRANDING, NO LOGO
Just pure Veo 3 output
"""

import sys
import os
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'

import time
from google import genai
from google.genai import types

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"  # Fast model: 20-60 seconds generation
LOCATION = "us-central1"

# Simple prompt
prompt = """
A professional working in a modern office with natural lighting.
Person typing on laptop, confident and focused.
Cinematic quality, realistic, vertical 9:16 format.
"""

print("="*70)
print("🎬 SIMPLE VEO 3 VIDEO GENERATION (NO BRANDING)")
print("="*70)
print(f"Model: {MODEL}")
print(f"Project: {PROJECT_ID}")
print(f"Prompt: {prompt.strip()}")
print("="*70)
print()

try:
    # Initialize client with Vertex AI
    print("🔐 Initializing Vertex AI client...")
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    print("✅ Client initialized\n")
    
    # Generate video
    print("📤 Sending video generation request...")
    print("⏳ Fast model: typically takes 20-60 seconds...\n")
    
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt.strip(),
        config=types.GenerateVideosConfig(
            aspect_ratio='9:16',
            number_of_videos=1,
            duration_seconds=8
        )
    )
    
    # Wait for completion
    start_time = time.time()
    check_count = 0
    
    while not operation.done:
        check_count += 1
        elapsed = int(time.time() - start_time)
        print(f"⏳ Generating... ({elapsed}s elapsed, check #{check_count})")
        time.sleep(10)  # Check every 10 seconds
        
        # Timeout after 3 minutes for fast model
        if elapsed > 180:
            print(f"\n❌ Timeout! Fast model should complete in 20-60s, took >{elapsed}s")
            sys.exit(1)
    
    print(f"\n✅ Generation complete! (took {int(time.time() - start_time)}s)\n")
    
    # Get result
    result = operation.result()
    
    if result.generated_videos:
        video_bytes = result.generated_videos[0].video.data
        
        # Save video
        output_path = "/app/output/videos/veo3_simple_test.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes) / (1024 * 1024)
        
        print("="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"📁 File: {output_path}")
        print(f"📊 Size: {file_size:.2f} MB")
        print(f"🌐 Live URL: https://vjgu.online/videos/videos/veo3_simple_test.mp4")
        print("="*70)
        
        # Also copy to generated_media for web access
        import shutil
        web_path = "/app/generated_media/videos/veo3_simple_test.mp4"
        os.makedirs(os.path.dirname(web_path), exist_ok=True)
        shutil.copy(output_path, web_path)
        print(f"📋 Copied to web directory: {web_path}")
        print("="*70)
        
    else:
        print("❌ No video in response")
        print(f"Response: {result}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
