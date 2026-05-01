#!/usr/bin/env python3
"""
Generate a branded 8-second video for Julia the Recruiter
using Vertex AI SDK (with Service Account) and MoviePy.
"""

import os
import sys
import time
import json
import numpy as np
from PIL import Image

# Monkeypatch for moviepy compatibility with newer Pillow
if not hasattr(Image, 'ANTIALIAS'):
    try:
        Image.ANTIALIAS = Image.Resampling.LANCZOS
    except AttributeError:
        # Fallback for very old Pillow if Resampling isn't there (unlikely)
        Image.ANTIALIAS = 1

# Path adjustments
BASE_DIR = "/root/.gemini/antigravity/scratch/social_automato"
APP_DIR = os.path.join(BASE_DIR, "app")
sys.path.insert(0, APP_DIR)

# Authentication
CREDENTIALS_PATH = os.path.join(APP_DIR, "google_credentials.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_PATH

from google import genai
from google.genai import types

# Configuration
PROJECT_ID = "julia-ai-automation"
MODEL = "veo-3.1-generate-preview" 
LOCATION = "us-central1"
ASSETS_DIR = os.path.join(APP_DIR, "assets")
OUTPUT_DIR = os.path.join(APP_DIR, "generated_media", "videos")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
# Fallback font
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Check for Montserrat
MONTSERRAT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-Bold.ttf")
if os.path.exists(MONTSERRAT_PATH):
    FONT_BOLD = MONTSERRAT_PATH

# User provided JSON text (first 8 seconds approx)
SUBTITLE_TEXT = "Are you currently looking for a new job and you feel overwhelmed because you just don't know where to start? If that is the case, I have the perfect product for you."

prompt = "A professional female recruiter named Julia in a modern bright office, looking at camera and talking, professional attire, high quality, cinematic, 9:16 aspect ratio"

w, h = 1080, 1920

def generate_video():
    print("="*70)
    print("🎬 STARTING VIDEO GENERATION (Vertex AI SDK + Service Account)")
    print("="*70)
    
    print(f"🔧 Using credentials from: {CREDENTIALS_PATH}")
    
    client = genai.Client(
        vertexai=True, 
        project=PROJECT_ID, 
        location=LOCATION
    )
    
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
    
    print(f"✅ Operation created: {operation.name}")
    print("⏳ Waiting for completion...")
    
    # Simple polling loop instead of .wait() to see progress
    start_time = time.time()
    while not operation.done:
        time.sleep(15)
        elapsed = int(time.time() - start_time)
        print(f"⏳ Elapsed: {elapsed}s...", end="\r")
        operation = client.operations.get(operation)
        if elapsed > 600:
            raise Exception("Timeout waiting for video generation")
            
    print("\n✅ Operation complete!")
    # In this SDK version, result seems to be a property
    result = operation.result
    
    if not result.generated_videos:
        raise Exception("No video generated")
        
    video_obj = result.generated_videos[0].video
    
    # Based on debug inspection, the attribute is 'video_bytes'
    if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
        print("✅ Found video content in 'video_bytes' attribute.")
        temp_video = os.path.join(APP_DIR, "generated_media", "temp_julia_8s_raw.mp4")
        os.makedirs(os.path.dirname(temp_video), exist_ok=True)
        with open(temp_video, "wb") as f:
            f.write(video_obj.video_bytes)
        return temp_video
        
    raise Exception(f"Could not find video data. Available attributes: {dir(video_obj)}")

def add_branding(video_path):
    print("🎨 Adding branding and subtitles...")
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips
    
    main_clip = VideoFileClip(video_path)
    
    # Ensure 9:16
    if main_clip.w != w or main_clip.h != h:
        main_clip = main_clip.resize(height=h)
        if main_clip.w < w:
            main_clip = main_clip.resize(width=w)
        main_clip = main_clip.crop(x1=main_clip.w/2 - w/2, x2=main_clip.w/2 + w/2, y1=0, y2=h)

    main_duration = main_clip.duration

    # Logo overlay
    logo_overlay = None
    if os.path.exists(LOGO_PATH):
        try:
            logo_img = Image.open(LOGO_PATH).convert('RGBA')
            logo_overlay = ImageClip(np.array(logo_img)).resize(width=200).set_opacity(0.9)
            logo_overlay = logo_overlay.set_position((w - 250, 80)).set_duration(main_duration)
        except Exception as e:
            print(f"⚠️ Could not add logo: {e}")

    # Subtitles
    try:
        subtitle_clip = TextClip(
            SUBTITLE_TEXT,
            fontsize=50,
            color='white',
            font=FONT_BOLD,
            size=(w-200, None),
            method='caption'
        ).set_position(('center', h - 400)).set_duration(main_duration)
        
        sub_bg = ColorClip(size=(w, 250), color=(0,0,0)).set_opacity(0.4).set_position(('center', h - 450)).set_duration(main_duration)
        
        clips_to_composite = [main_clip]
        if logo_overlay:
            clips_to_composite.append(logo_overlay)
        clips_to_composite.extend([sub_bg, subtitle_clip])
    except Exception as e:
        print(f"⚠️ Subtitle generation failed: {e}. Proceeding without subtitles.")
        clips_to_composite = [main_clip]
        if logo_overlay:
            clips_to_composite.append(logo_overlay)
    
    main_body = CompositeVideoClip(clips_to_composite).set_duration(main_duration)

    # Intro (1.5s)
    intro_duration = 1.5
    intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
    
    intro_clips = [intro_bg]
    try:
        intro_text = TextClip("HR SUCCESS TIPS", fontsize=80, color='black', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 200)).set_duration(intro_duration)
        intro_clips.append(intro_text)
    except: pass
    
    if os.path.exists(LOGO_PATH):
        try:
            intro_logo = ImageClip(np.array(Image.open(LOGO_PATH).convert('RGBA'))).resize(width=500).set_position('center').set_duration(intro_duration)
            intro_clips.append(intro_logo)
        except: pass
    
    intro_scene = CompositeVideoClip(intro_clips)

    # Outro (3.5s)
    outro_duration = 3.5
    outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)
    
    outro_clips = [outro_bg]
    try:
        outro_text = TextClip("VirtualJobGuru\nYour Career. Your Growth.", fontsize=60, color='white', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 200)).set_duration(outro_duration)
        outro_clips.append(outro_text)
    except: pass
    
    if os.path.exists(LOGO_PATH):
        try:
            outro_logo = ImageClip(np.array(Image.open(LOGO_PATH).convert('RGBA'))).resize(width=450).set_position('center').set_duration(outro_duration)
            outro_clips.append(outro_logo)
        except: pass
    
    outro_scene = CompositeVideoClip(outro_clips)

    print("🎥 Assembling final video...")
    final_video = concatenate_videoclips([intro_scene, main_body, outro_scene])
    
    output_filename = "branded_julia_8s.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    return output_path

if __name__ == "__main__":
    try:
        raw_video_path = os.path.join(APP_DIR, "generated_media", "temp_julia_8s_raw.mp4")
        
        if os.path.exists(raw_video_path) and os.path.getsize(raw_video_path) > 0:
            print(f"🎬 Found existing raw video at {raw_video_path}, skipping generation...")
            raw_video = raw_video_path
        else:
            raw_video = generate_video()
            
        final_video = add_branding(raw_video)
        print("="*70)
        print("✅ SUCCESS!")
        print(f"📁 Video saved to: {final_video}")
        print(f"🌐 URL: https://vjgu.online/videos/videos/branded_julia_8s.mp4")
        print("="*70)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
