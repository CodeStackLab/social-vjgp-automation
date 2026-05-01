#!/usr/bin/env python3
"""
Simple single video test - Veo 3 Fast
"""

import sys
import os
import time
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

from google import genai
from google.genai.types import GenerateVideosConfig

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"

prompt = "A professional HR expert speaking confidently in a modern office, natural lighting, cinematic, vertical 9:16"

print("="*70)
print("🎬 SINGLE VIDEO TEST - VEO 3 FAST")
print("="*70)
print(f"Prompt: {prompt}")
print("="*70)
print()

client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')

print("📤 Starting generation...")
operation = client.models.generate_videos(
    model=MODEL,
    prompt=prompt,
    config=GenerateVideosConfig(aspect_ratio='9:16')
)

print(f"✅ Operation: {operation.name}\n")

# Poll
while not operation.done:
    print("⏳ Generating...", flush=True)
    time.sleep(15)
    operation = client.operations.get(operation)

print("\n✅ Complete!\n")

# Save
if operation.result and operation.result.generated_videos:
    video_bytes = operation.result.generated_videos[0].video.video_bytes
    
    output_path = "/app/output/videos/veo3_single_test.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "wb") as f:
        f.write(video_bytes)
    
    size_mb = len(video_bytes) / (1024 * 1024)
    
    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"📁 File: {output_path}")
    print(f"📊 Size: {size_mb:.2f} MB")
    print(f"🌐 URL: https://vjgu.online/videos/veo3_single_test.mp4")
    print("="*70)
else:
    print("❌ No video generated")
