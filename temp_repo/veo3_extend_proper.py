#!/usr/bin/env python3
"""
Veo 3 Video Extension - Proper Implementation
Extends existing video to maintain character consistency
Uses GCS bucket for video storage as per official documentation
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
from google.genai.types import GenerateVideosConfig, Video
from google.cloud import storage

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"
BUCKET_NAME = "vjgu-video-generation"  # Create this bucket
LOCATION = "us-central1"

def upload_to_gcs(local_path, gcs_path):
    """Upload video to GCS bucket"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        blob.upload_from_filename(local_path)
        
        gcs_uri = f"gs://{BUCKET_NAME}/{gcs_path}"
        print(f"✅ Uploaded to: {gcs_uri}")
        return gcs_uri
    except Exception as e:
        print(f"❌ GCS upload error: {e}")
        return None

def download_from_gcs(gcs_uri, local_path):
    """Download video from GCS"""
    try:
        # Parse GCS URI
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1]
        
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        blob.download_to_filename(local_path)
        print(f"✅ Downloaded to: {local_path}")
        return local_path
    except Exception as e:
        print(f"❌ GCS download error: {e}")
        return None

def generate_base_video(prompt, output_gcs_path):
    """Generate initial 8s video"""
    print("\n🎬 Generating base video...")
    
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=GenerateVideosConfig(
            aspect_ratio='9:16',
            output_gcs_uri=output_gcs_path
        )
    )
    
    print(f"Operation: {operation.name}")
    
    # Poll for completion
    while not operation.done:
        print("⏳ Generating...", flush=True)
        time.sleep(15)
        operation = client.operations.get(operation)
    
    if operation.result and operation.result.generated_videos:
        video_uri = operation.result.generated_videos[0].video.uri
        print(f"✅ Base video generated: {video_uri}")
        return video_uri
    
    return None

def extend_video(base_video_uri, extension_prompt, output_gcs_path):
    """Extend existing video to maintain character consistency"""
    print(f"\n🔄 Extending video...")
    print(f"Base: {base_video_uri}")
    print(f"Prompt: {extension_prompt}")
    
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    # CRITICAL: Use Video object with uri parameter
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=extension_prompt,
        video=Video(
            uri=base_video_uri,
            mime_type="video/mp4"
        ),
        config=GenerateVideosConfig(
            output_gcs_uri=output_gcs_path
        )
    )
    
    print(f"Operation: {operation.name}")
    
    # Poll for completion
    while not operation.done:
        print("⏳ Extending...", flush=True)
        time.sleep(15)
        operation = client.operations.get(operation)
    
    if operation.result and operation.result.generated_videos:
        video_uri = operation.result.generated_videos[0].video.uri
        print(f"✅ Extended video: {video_uri}")
        return video_uri
    
    return None

def create_extended_video_with_consistency(
    base_prompt,
    extension_prompts,
    topic="HR Career Tips"
):
    """
    Create extended video with character consistency
    
    Args:
        base_prompt: Initial video prompt with character definition
        extension_prompts: List of prompts for extensions
        topic: Topic for naming
    """
    print("="*70)
    print("🎬 VEO 3 VIDEO EXTENSION - CHARACTER CONSISTENCY")
    print("="*70)
    print(f"Topic: {topic}")
    print(f"Total segments: {len(extension_prompts) + 1}")
    print("="*70)
    
    timestamp = int(time.time())
    
    # Step 1: Generate base video
    base_gcs_path = f"videos/base_{timestamp}.mp4"
    base_gcs_uri = f"gs://{BUCKET_NAME}/{base_gcs_path}"
    
    base_video_uri = generate_base_video(base_prompt, base_gcs_uri)
    
    if not base_video_uri:
        print("❌ Failed to generate base video")
        return None
    
    # Step 2: Extend video multiple times
    current_video_uri = base_video_uri
    
    for i, ext_prompt in enumerate(extension_prompts, 1):
        ext_gcs_path = f"videos/extended_{timestamp}_part{i}.mp4"
        ext_gcs_uri = f"gs://{BUCKET_NAME}/{ext_gcs_path}"
        
        extended_uri = extend_video(current_video_uri, ext_prompt, ext_gcs_uri)
        
        if not extended_uri:
            print(f"❌ Failed to extend video (part {i})")
            break
        
        current_video_uri = extended_uri
        print(f"✅ Part {i+1}/{len(extension_prompts)+1} complete")
    
    # Step 3: Download final video
    final_local_path = f"/app/generated_media/videos/extended_consistent_{timestamp}.mp4"
    os.makedirs(os.path.dirname(final_local_path), exist_ok=True)
    
    if download_from_gcs(current_video_uri, final_local_path):
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"📁 Local: {final_local_path}")
        print(f"☁️  GCS: {current_video_uri}")
        print(f"🌐 URL: https://vjgu.online/videos/videos/{os.path.basename(final_local_path)}")
        print("="*70)
        return final_local_path
    
    return None

if __name__ == "__main__":
    # Character definition (English only)
    character = "a professional HR consultant in her early 40s, warm and confident smile, wearing a navy blue blazer over white blouse, modern corporate office with glass walls and green plants in background, natural daylight from large windows"
    
    # Base prompt (8 seconds)
    base_prompt = f"{character}, speaking directly to camera about interview preparation, gesturing naturally with hands, medium close-up shot, professional lighting, cinematic quality, clear English audio with professional tone"
    
    # Extension prompts (each adds ~8 seconds)
    extension_prompts = [
        f"{character}, continuing to speak about resume tips, maintaining eye contact with camera, same office setting, smooth continuation of previous segment, clear English audio",
        f"{character}, concluding with career advice, nodding encouragingly, same professional demeanor and setting, wrapping up the discussion, clear English audio"
    ]
    
    # Generate extended video (24 seconds total)
    create_extended_video_with_consistency(
        base_prompt,
        extension_prompts,
        topic="Interview Success Tips"
    )
