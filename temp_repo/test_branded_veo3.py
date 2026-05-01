#!/usr/bin/env python3
"""
Test branded video generation with Veo 3 Fast
"""

import sys
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine

# Test configuration
PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"

# Test prompt
test_prompt = """
A professional HR expert speaking confidently to camera in a modern office.
Natural lighting, professional attire, engaging presentation.
Cinematic quality, vertical 9:16 format.
"""

print("="*70)
print("🎬 TESTING BRANDED VIDEO WITH VEO 3 FAST")
print("="*70)
print()

# Generate branded video with all features
video_path, filename = video_engine.create_branded_video(
    script_text=test_prompt,
    title="HR Success Tips",
    model_name=MODEL,
    project_id=PROJECT_ID
)

print()
print("="*70)
if video_path:
    print("✅ SUCCESS!")
    print(f"📁 Video: {video_path}")
    print(f"📋 Filename: {filename}")
    print("="*70)
else:
    print("❌ FAILED!")
    print("="*70)
