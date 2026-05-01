"""
Complete Workflow: Research → Script → Extended Video → Social Posting
Integrates Perplexity, Gemini, Veo Extension, and Social Media
"""

import os
import sys
import time
import json
sys.path.insert(0, '/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

import research_engine
from google import genai
from google.genai.types import GenerateVideosConfig, Video
from google.cloud import storage
from moviepy.editor import *
import numpy as np
from PIL import Image

# Configuration
PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"
BUCKET_NAME = "vjgu-video-generation"
LOCATION = "us-central1"
OUTPUT_DIR = "/app/generated_media/videos"
ASSETS_DIR = "/app/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"

w, h = 1080, 1920

def upload_to_gcs(local_path, gcs_path):
    """Upload file to GCS"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        return f"gs://{BUCKET_NAME}/{gcs_path}"
    except Exception as e:
        print(f"GCS upload error: {e}")
        return None

def download_from_gcs(gcs_uri, local_path):
    """Download file from GCS"""
    try:
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket_name, blob_path = parts[0], parts[1]
        
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.download_to_filename(local_path)
        return local_path
    except Exception as e:
        print(f"GCS download error: {e}")
        return None

def generate_video_with_extension(
    base_prompt,
    extension_count=2,
    output_gcs_prefix="videos/extended"
):
    """
    Generate extended video with character consistency
    
    Args:
        base_prompt: Initial prompt with character definition (English only)
        extension_count: Number of 7s extensions to add
        output_gcs_prefix: GCS path prefix
        
    Returns:
        Final video GCS URI
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    timestamp = int(time.time())
    
    # Generate base video (8s)
    print(f"🎬 Generating base video (8s)...")
    base_gcs_uri = f"gs://{BUCKET_NAME}/{output_gcs_prefix}_base_{timestamp}.mp4"
    
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=base_prompt,
        config=GenerateVideosConfig(
            aspect_ratio='9:16',
            output_gcs_uri=base_gcs_uri
        )
    )
    
    while not operation.done:
        time.sleep(15)
        operation = client.operations.get(operation)
    
    if not operation.result or not operation.result.generated_videos:
        print("❌ Base video generation failed")
        return None
    
    current_uri = operation.result.generated_videos[0].video.uri
    print(f"✅ Base video: {current_uri}")
    
    # Extend video multiple times
    for i in range(extension_count):
        print(f"🔄 Extension {i+1}/{extension_count} (adding 7s)...")
        ext_gcs_uri = f"gs://{BUCKET_NAME}/{output_gcs_prefix}_ext{i+1}_{timestamp}.mp4"
        
        # Extension prompt should maintain character consistency
        ext_prompt = base_prompt.replace("speaking about", f"continuing to speak about")
        
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=ext_prompt,
            video=Video(uri=current_uri, mime_type="video/mp4"),
            config=GenerateVideosConfig(output_gcs_uri=ext_gcs_uri)
        )
        
        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
        
        if not operation.result or not operation.result.generated_videos:
            print(f"❌ Extension {i+1} failed")
            break
        
        current_uri = operation.result.generated_videos[0].video.uri
        print(f"✅ Extended to: {8 + (i+1)*7}s")
    
    return current_uri

def add_branding_to_video(video_path, client_details, script_data):
    """Add branding, subtitles, and client info to video"""
    
    # Load video
    main_clip = VideoFileClip(video_path)
    
    # Resize to 9:16
    if main_clip.w != w or main_clip.h != h:
        main_clip = main_clip.resize(height=h)
        if main_clip.w < w:
            main_clip = main_clip.resize(width=w)
        main_clip = main_clip.crop(x1=main_clip.w/2 - w/2, x2=main_clip.w/2 + w/2, y1=0, y2=h)
    
    duration = main_clip.duration
    
    # Random logo
    import random
    logos = [os.path.join(PNG_DIR, f) for f in os.listdir(PNG_DIR) if f.endswith('.png')]
    logo_path = random.choice(logos) if logos else None
    
    # Logo overlay
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert('RGB')
        logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
        logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(duration)
    else:
        logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration).set_opacity(0)
    
    # Subtitles from script
    subtitle_clips = []
    title = script_data.get('title', 'Career Tips')
    
    # Title subtitle
    sub1 = TextClip(
        title.upper(),
        fontsize=60,
        color='#FFD700',
        font=FONT_BOLD,
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(w-100, None),
        align='center'
    ).set_position(('center', h - 400)).set_start(1).set_duration(3)
    subtitle_clips.append(sub1)
    
    # Contact info overlay (if enabled)
    if client_details.get('branding', {}).get('show_contact_in_video'):
        contact = client_details.get('contact_info', {})
        contact_text = f"{contact.get('website', '')} | {contact.get('city', '')}"
        
        contact_clip = TextClip(
            contact_text,
            fontsize=35,
            color='#FFFFFF',
            font=FONT_BOLD,
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(w-100, None),
            align='center'
        ).set_position(('center', h - 150)).set_start(duration - 5).set_duration(5)
        subtitle_clips.append(contact_clip)
    
    # Composite
    final_clip = CompositeVideoClip([main_clip, logo_overlay] + subtitle_clips)
    
    # Add intro/outro
    intro_duration = 1.5
    intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
    
    if logo_path and os.path.exists(logo_path):
        intro_logo_img = Image.open(logo_path).convert('RGB')
        intro_logo = ImageClip(np.array(intro_logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
    else:
        intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)
    
    intro_text = TextClip(title.upper(), fontsize=70, color='#000000', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
    intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])
    
    # Outro
    outro_duration = 3.5
    outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)
    
    if logo_path and os.path.exists(logo_path):
        outro_logo_img = Image.open(logo_path).convert('RGB')
        outro_logo = ImageClip(np.array(outro_logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
    else:
        outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)
    
    outro_text = TextClip("VirtualJobGuru\\nYour Career. Your Growth.", fontsize=55, color='#FFFFFF', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 300)).set_duration(outro_duration)
    outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])
    
    # Final video
    final_video = concatenate_videoclips([intro_scene, final_clip, outro_composite])
    
    return final_video

def complete_workflow(
    topic,
    perplexity_key,
    gemini_key,
    client_details,
    extension_count=2
):
    """
    Complete workflow from research to final video
    
    Args:
        topic: Research topic (English)
        perplexity_key: Perplexity API key
        gemini_key: Gemini API key
        client_details: Client details dict
        extension_count: Number of extensions (each adds 7s)
        
    Returns:
        Dict with video path, social content, etc.
    """
    print("="*70)
    print("🚀 COMPLETE WORKFLOW: RESEARCH → SCRIPT → VIDEO → SOCIAL")
    print("="*70)
    print(f"Topic: {topic}")
    print(f"Target duration: {8 + extension_count * 7}s")
    print("="*70)
    print()
    
    # Step 1: Research with Perplexity
    print("📚 Step 1: Researching topic...")
    research_result = research_engine.perplexity_research(topic, perplexity_key)
    
    if not research_result['success']:
        print(f"❌ Research failed: {research_result.get('error')}")
        return None
    
    print(f"✅ Research complete")
    
    # Step 2: Generate script with Gemini
    print("\\n📝 Step 2: Generating script...")
    script_result = research_engine.gemini_generate_script(
        research_result,
        client_details,
        gemini_key,
        duration=8 + extension_count * 7
    )
    
    if not script_result['success']:
        print(f"❌ Script generation failed: {script_result.get('error')}")
        return None
    
    print(f"✅ Script generated: {script_result['script'].get('title')}")
    
    # Step 3: Create character prompt (English only)
    character = script_result['character']
    base_prompt = f"{character}, speaking directly to camera in clear English, professional tone, medium close-up shot, cinematic lighting, 4k quality"
    
    # Step 4: Generate extended video
    print("\\n🎬 Step 3: Generating extended video...")
    final_gcs_uri = generate_video_with_extension(
        base_prompt,
        extension_count=extension_count
    )
    
    if not final_gcs_uri:
        print("❌ Video generation failed")
        return None
    
    # Download from GCS
    timestamp = int(time.time())
    local_path = f"{OUTPUT_DIR}/workflow_{timestamp}.mp4"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\\n⬇️  Downloading from GCS...")
    if not download_from_gcs(final_gcs_uri, local_path):
        print("❌ Download failed")
        return None
    
    print(f"✅ Downloaded: {local_path}")
    
    # Step 5: Add branding
    print("\\n🎨 Step 4: Adding branding...")
    branded_video = add_branding_to_video(local_path, client_details, script_result['script'])
    
    final_path = f"{OUTPUT_DIR}/final_workflow_{timestamp}.mp4"
    branded_video.write_videofile(
        final_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        bitrate="8000k",
        preset='medium',
        threads=4,
        logger=None,
        ffmpeg_params=['-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
    )
    
    print(f"✅ Branded video: {final_path}")
    
    # Step 6: Generate social content
    print("\\n📱 Step 5: Generating social content...")
    social_content = {}
    
    for platform in ['instagram', 'tiktok', 'youtube']:
        result = research_engine.gemini_generate_social_content(
            script_result['script'],
            platform,
            gemini_key
        )
        if result['success']:
            social_content[platform] = result['content']
    
    print(f"✅ Social content generated for {len(social_content)} platforms")
    
    # Summary
    print("\\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70)
    print(f"📁 Video: {final_path}")
    print(f"📋 Filename: {os.path.basename(final_path)}")
    print(f"⏱️  Duration: ~{8 + extension_count * 7 + 5}s (with intro/outro)")
    print(f"🌐 URL: https://vjgu.online/videos/videos/{os.path.basename(final_path)}")
    print("\\n📱 Social Content:")
    for platform, content in social_content.items():
        print(f"  {platform.capitalize()}: {content.get('title', 'N/A')}")
    print("="*70)
    
    return {
        "video_path": final_path,
        "video_url": f"https://vjgu.online/videos/videos/{os.path.basename(final_path)}",
        "research": research_result,
        "script": script_result,
        "social_content": social_content,
        "duration": 8 + extension_count * 7 + 5
    }

# Example usage
if __name__ == "__main__":
    # Load client details from config
    import json
    
    client_details = {
        "character_profile": {
            "name": "HR Professional",
            "profession": "professional HR consultant in her early 40s",
            "appearance": "warm confident smile, navy blue blazer over white blouse",
            "setting": "modern corporate office with glass walls and green plants, natural daylight"
        },
        "contact_info": {
            "phone": "+49 1577 4331858",
            "email": "info@virtualjobguru.com",
            "website": "www.virtualjobguru.com",
            "city": "Berlin, Germany"
        },
        "branding": {
            "show_contact_in_video": True
        }
    }
    
    # Example: Run workflow
    # result = complete_workflow(
    #     topic="How to answer behavioral interview questions",
    #     perplexity_key="pplx-xxx",
    #     gemini_key="AIza-xxx",
    #     client_details=client_details,
    #     extension_count=2  # 8s base + 2x7s = 22s total
    # )
    
    print("✅ Workflow module loaded. Ready to use.")
