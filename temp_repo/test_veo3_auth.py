#!/usr/bin/env python3
"""
Veo 3 Test with Service Account Authentication
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine

# Set Google Application Credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'

# Test configuration
PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-generate-preview"

# Test prompt - simple and clear
test_prompt = """
A modern professional office with natural sunlight. 
A person working confidently at a desk with a laptop.
Cinematic, high quality, vertical 9:16 format.
"""

print("="*70)
print("🎬 VEO 3 FAST VIDEO GENERATION TEST")
print("="*70)
print(f"Model: {MODEL}")
print(f"Project ID: {PROJECT_ID}")
print(f"Auth: Service Account (google_credentials.json)")
print(f"Prompt: {test_prompt.strip()}")
print("="*70)
print()

# Generate video using project_id (not API key)
print("📤 Starting video generation with service account auth...")
print("⏳ This may take 2-5 minutes...")
print()

video_path = video_engine.generate_video_asset(
    prompt=test_prompt.strip(),
    project_id=PROJECT_ID,
    model_name=MODEL,
    api_key=None  # Use service account instead
)

print()
print("="*70)

if video_path and os.path.exists(video_path):
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    print("✅ SUCCESS! Video generated successfully!")
    print("="*70)
    print(f"📁 File: {video_path}")
    print(f"📊 Size: {file_size:.2f} MB")
    print(f"🔗 View: file://{video_path}")
    print("="*70)
    
    # Copy to output directory for easy access
    import shutil
    output_file = "/app/output/videos/veo3_test_output.mp4"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    shutil.copy(video_path, output_file)
    print(f"📋 Copied to: {output_file}")
    print("="*70)
else:
    print("❌ FAILED! Video generation unsuccessful")
    print("="*70)
    if video_path:
        print(f"Expected path: {video_path}")
    print("Check logs above for error details")
    print("="*70)
