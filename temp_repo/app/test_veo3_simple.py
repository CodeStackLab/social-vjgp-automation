#!/usr/bin/env python3
"""
Simple Veo 3 Test - Using existing video_engine module
Tests video generation without any branding or post-processing
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine

# Test configuration
PROJECT_ID = "your-project-id"
API_KEY = "YOUR_API_KEY"
MODEL = "veo-3.1-generate-preview"

# Test prompt
test_prompt = """
A professional office environment with modern furniture and natural lighting. 
A confident professional working at a desk with a laptop. 
Cinematic quality, vertical 9:16 format, realistic, high-quality.
""".strip()

print("="*70)
print("🎬 VEO 3 FAST VIDEO GENERATION TEST")
print("="*70)
print(f"Model: {MODEL}")
print(f"Project ID: {PROJECT_ID}")
print(f"Prompt: {test_prompt}")
print("="*70)
print()

# Generate video using existing function
print("📤 Starting video generation...")
print()

video_path = video_engine.generate_video_asset(
    prompt=test_prompt,
    project_id=PROJECT_ID,
    model_name=MODEL,
    api_key=API_KEY
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
else:
    print("❌ FAILED! Video generation unsuccessful")
    print("="*70)
    if video_path:
        print(f"Expected path: {video_path}")
    print("Check logs above for error details")
    print("="*70)
