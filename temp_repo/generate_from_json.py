#!/usr/bin/env python3
"""
Generate Branded Video from JSON Input (Future/Scheduled Flow)
"""

import sys
import os
import json
import random
import time
from moviepy.editor import *
import numpy as np
from PIL import Image

# Ensure app directory is in path
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_media", "videos")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")
FONT_BOLD = os.path.join(ASSETS_DIR, "fonts", "Montserrat-Bold.ttf")

# Check if paths exist, fallback to /app if not (container compatibility)
if not os.path.exists(OUTPUT_DIR):
    OUTPUT_DIR = "/app/generated_media/videos"
if not os.path.exists(ASSETS_DIR):
    ASSETS_DIR = "/app/assets"
    PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")
    FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"

# Colors (Tuples for MoviePy)
PRIMARY_ORANGE = (255, 141, 31)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Default JSON for testing/example
EXAMPLE_JSON = {
    "text": " Are you currently looking for a new job and you feel overwhelmed because you just don't know where to start? If that is the case, I have the perfect product for you. My name is Julia and I've been working as a recruiter for the last 20 years. In my one-to-one coaching session, I will guide you step-by-step through the entire process. We will check all your documents and I can guarantee you I will help you in the best way possible. If you're interested, click on the link below.",
    "segments": [
        {"id": 0, "seek": 0, "start": 0.0, "end": 5.5, "text": " Are you currently looking for a new job and you feel overwhelmed because you just don't know where to start?", "tokens": [], "temperature": 0.0, "avg_logprob": -0.13, "compression_ratio": 1.58, "no_speech_prob": 0.08},
        {"id": 1, "seek": 0, "start": 5.5, "end": 9.0, "text": " If that is the case, I have the perfect product for you.", "tokens": [], "temperature": 0.0, "avg_logprob": -0.13, "compression_ratio": 1.58, "no_speech_prob": 0.08},
        {"id": 2, "seek": 0, "start": 9.0, "end": 14.0, "text": " My name is Julia and I've been working as a recruiter for the last 20 years.", "tokens": [], "temperature": 0.0, "avg_logprob": -0.13, "compression_ratio": 1.58, "no_speech_prob": 0.08}
    ],
    "language": "en"
}

def generate_video_from_json(json_data):
    print("=" * 60)
    print("🎬 GENERATING BRANDED VIDEO FROM JSON")
    print("=" * 60)

    # 1. Parse JSON to get prompt context
    full_text = json_data.get('text', '')
    segments = json_data.get('segments', [])
    
    print(f"📝 Full Text: {full_text[:100]}...")
    
    visual_prompt = f"Cinematic professional shot, corporate office environment, HR context: {full_text[:50]}"
    print(f"🎨 Visual Prompt for Veo: {visual_prompt}")

    # 2. Get Credentials
    project_id = None
    
    # Priority: Check for explicit credentials file first
    creds_path = os.path.join(os.path.dirname(__file__), 'app', 'google_credentials.json')
    if not os.path.exists(creds_path):
        creds_path = '/app/google_credentials.json'

    if os.path.exists(creds_path):
        print(f"🔑 Found credentials file: {creds_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
                project_id = creds_data.get('project_id')
                print(f"🔑 Using Project ID: {project_id}")
        except Exception as e:
            print(f"⚠️ Error reading credentials file: {e}")

    # Fallback to app_settings if project_id still missing
    if not project_id:
        settings_path = '/app/data/app_settings.json'
        if not os.path.exists(settings_path):
            settings_path = os.path.join(os.path.dirname(__file__), 'data', 'app_settings.json')

        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    val = settings.get('api_config', {}).get('vertex_project_id')
                    if val and val != "your-project-id":
                        project_id = val
                    
                    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                        creds_json = settings.get('api_config', {}).get('google_cloud_json')
                        if creds_json:
                            tmp_creds_path = "/tmp/gcp_creds.json"
                            if isinstance(creds_json, str):
                                with open(tmp_creds_path, "w") as cf:
                                    cf.write(creds_json)
                            else:
                                with open(tmp_creds_path, "w") as cf:
                                    json.dump(creds_json, cf)
                            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_creds_path
        except Exception as e:
            print(f"⚠️ Error loading settings: {e}")

    # 3. Generate Video
    print("🚀 Requesting Video Generation...")
    video_path, filename = video_engine.create_branded_video(
        script_text=full_text, 
        title="Automated Clip",
        visual_prompt=visual_prompt,
        model_name="veo-3.1-generate-preview",
        api_key=None,
        project_id=project_id,
        target_clips=1,
        skip_branding=True
    )

    if not video_path:
        print("❌ Failed to generate base video.")
        return

    print(f"✅ Base Video Generated: {video_path}")

    # 4. Apply Branding & Subtitles
    output_path = apply_json_branding(video_path, segments)
    
    if output_path:
        print("\n" + "=" * 60)
        print("✅ FINAL VIDEO COMPLETE")
        print(f"📁 Path: {output_path}")
        print(f"🌐 URL: https://vjgu.online/videos/videos/{os.path.basename(output_path)}")
        print("=" * 60)

def apply_json_branding(video_path, segments):
    print("🎨 Applying Branding & Subtitles...")
    
    try:
        main_clip = VideoFileClip(video_path)
        w, h = 1080, 1920
        
        # Resize/Crop to 9:16
        if main_clip.w != w or main_clip.h != h:
            main_clip = main_clip.resize(height=h)
            if main_clip.w < w:
                main_clip = main_clip.resize(width=w)
            main_clip = main_clip.crop(x1=main_clip.w/2 - w/2, x2=main_clip.w/2 + w/2, y1=0, y2=h)
        
        duration = main_clip.duration

        # --- Branding Elements ---
        # 1. Logo
        logos = []
        if os.path.exists(PNG_DIR):
            for f in os.listdir(PNG_DIR):
                if f.lower().endswith('.png'):
                    logos.append(os.path.join(PNG_DIR, f))
        
        selected_logo = random.choice(logos) if logos else None
        
        logo_overlay = None
        if selected_logo:
             logo_img = Image.open(selected_logo).convert('RGB')
             logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
             logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(duration)

        # 2. Subtitles from JSON
        subtitle_clips = []
        print("📝 Generating Subtitles from JSON Segments...")
        for seg in segments:
            start = seg.get('start', 0)
            end = seg.get('end', 0)
            text = seg.get('text', '').strip()
            
            if start > duration:
                continue
            if end > duration:
                end = duration
            
            if text:
                txt_clip = TextClip(
                    text,
                    fontsize=55,
                    color='white',
                    font=FONT_BOLD,
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(w-100, None),
                    align='center'
                ).set_position(('center', h - 400)).set_start(start).set_duration(end - start)
                subtitle_clips.append(txt_clip)

        # 3. Intro/Outro (Fast version)
        intro_duration = 1.0
        intro_bg = ColorClip(size=(w, h), color=PRIMARY_ORANGE, duration=intro_duration)
        intro_text = TextClip("NEW UPDATE", fontsize=70, color='black', font=FONT_BOLD, stroke_color='white', stroke_width=2, method='caption', size=(w-100, None)).set_position('center').set_duration(intro_duration)
        intro_scene = CompositeVideoClip([intro_bg, intro_text])

        outro_duration = 2.0
        outro_bg = ColorClip(size=(w, h), color=BLACK, duration=outro_duration)
        outro_text = TextClip("VirtualJobGuru\nFollow for more", fontsize=60, color='white', font=FONT_BOLD, method='caption', size=(w-100, None)).set_position('center').set_duration(outro_duration)
        outro_scene = CompositeVideoClip([outro_bg, outro_text])

        # Composite Main Body
        clips_to_composite = [main_clip]
        if logo_overlay:
            clips_to_composite.append(logo_overlay)
        clips_to_composite.extend(subtitle_clips)
        
        main_body = CompositeVideoClip(clips_to_composite).set_duration(duration)

        # Final Concatenate
        final_video = concatenate_videoclips([intro_scene, main_body, outro_scene])
        
        # Output
        output_filename = f"json_branded_{int(time.time())}.mp4"
        output_full_path = os.path.join(OUTPUT_DIR, output_filename)
        
        final_video.write_videofile(
            output_full_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            bitrate="8000k",
            threads=4,
            preset='fast',
            logger=None
        )
        
        return output_full_path

    except Exception as e:
        print(f"❌ Error applying branding: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                input_data = json.load(f)
                generate_video_from_json(input_data)
        except Exception as e:
            print(f"Error reading input file: {e}")
    else:
        print("Using built-in EXAMPLE JSON")
        generate_video_from_json(EXAMPLE_JSON)
