#!/usr/bin/env python3
"""Quick test script to verify video generation with new subtitle features"""

import sys
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine
import os

# Initialize Vertex AI
creds = video_engine.init_vertex(
    credentials_json=None,
    project_id=os.getenv("GCP_PROJECT_ID")
)

print("=" * 60)
print("🎬 TESTING VIDEO GENERATION WITH AUTO-SUBTITLES")
print("=" * 60)

# Test Script
test_script = "Master your interview skills with VirtualJobGuru. Your career growth starts here."

print(f"\n📝 Script: {test_script}")
print("\n⏳ Generating video (this will take ~1-2 minutes)...\n")

# Generate Video
video_path, filename = video_engine.create_branded_video(
    script_text=test_script,
    title="Interview Tips",
    visual_prompt=None,
    creds=creds
)

if video_path and os.path.exists(video_path):
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    print("\n" + "=" * 60)
    print(f"✅ SUCCESS! Video Generated")
    print(f"📁 Path: {video_path}")
    print(f"📦 Size: {file_size:.2f} MB")
    print(f"🌐 URL: https://vjgu.online/videos/videos/{filename}")
    print("=" * 60)
else:
    print("\n❌ FAILED: Video generation failed")
    print(f"Error: {filename}")
