#!/usr/bin/env python3
"""
Test video generation with updated Vertex AI credentials
"""
import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import video_engine

def main():
    print("=" * 60)
    print("Testing Vertex AI Video Generation")
    print("=" * 60)
    
    # Test parameters
    project_id = "julia-ai-automation"
    model_name = "veo-3.1-fast-generate-001"
    prompt = "A professional HR recruiter sitting in a modern office, speaking confidently to camera, cinematic lighting, high quality"
    
    print(f"\n📋 Configuration:")
    print(f"  Project ID: {project_id}")
    print(f"  Model: {model_name}")
    print(f"  Prompt: {prompt}")
    print(f"  Duration: 8 seconds")
    print(f"  Aspect Ratio: 9:16 (portrait)")
    
    print(f"\n🎬 Starting video generation...")
    print(f"⏱️  This may take 2-3 minutes...\n")
    
    start_time = time.time()
    
    try:
        video_path = video_engine.generate_video_asset(
            prompt=prompt,
            project_id=project_id,
            model_name=model_name
        )
        
        elapsed_time = time.time() - start_time
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"\n✅ SUCCESS!")
            print(f"  Video saved to: {video_path}")
            print(f"  File size: {file_size:.2f} MB")
            print(f"  Generation time: {elapsed_time:.1f} seconds")
            print(f"\n🎥 You can view the video at:")
            print(f"  https://vjgu.online/videos/{os.path.basename(video_path)}")
            return 0
        else:
            print(f"\n❌ FAILED: Video generation did not return a valid file")
            print(f"  Generation time: {elapsed_time:.1f} seconds")
            return 1
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ ERROR: {e}")
        print(f"  Generation time: {elapsed_time:.1f} seconds")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
