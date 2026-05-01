#!/usr/bin/env python3
"""
Generate extended video (20-30 seconds) using multiple 8s clips
Uses existing Veo 3 Fast implementation with parallel generation
"""

import sys
import os
import time
import random
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

from google import genai
from google.genai.types import GenerateVideosConfig
from moviepy.editor import *
import numpy as np
from PIL import Image
import concurrent.futures

PROJECT_ID = "your-project-id"
MODEL = "veo-3.1-fast-generate-001"
ASSETS_DIR = "/app/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "logo")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"
OUTPUT_DIR = "/app/generated_media/videos"

w, h = 1080, 1920

# HR prompts for variety
hr_prompts = [
    "A professional HR expert speaking confidently in a modern office, natural lighting, cinematic",
    "A career coach giving advice with a tablet, professional setting, engaging presentation",
    "An HR manager reviewing documents and smiling, corporate environment, professional",
    "A business mentor explaining concepts at a whiteboard, modern office, dynamic"
]

def generate_single_clip(prompt, index):
    """Generate a single 8s clip"""
    print(f"🎬 Generating clip {index+1}...", flush=True)
    
    client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')
    
    full_prompt = f"{prompt}, high quality, 9:16 vertical, cinematic, professional lighting"
    
    operation = client.models.generate_videos(
        model=MODEL,
        prompt=full_prompt,
        config=GenerateVideosConfig(aspect_ratio='9:16')
    )
    
    # Poll for completion
    while not operation.done:
        time.sleep(15)
        operation = client.operations.get(operation)
    
    # Save video
    if operation.result and operation.result.generated_videos:
        video_bytes = operation.result.generated_videos[0].video.video_bytes
        
        temp_path = f"/app/generated_media/temp/extended_clip_{index}_{int(time.time())}.mp4"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(video_bytes)
        
        print(f"✅ Clip {index+1} complete!", flush=True)
        return temp_path
    
    return None

def create_extended_video(num_clips=3, topic="HR Success Tips"):
    """Create 20-30s video with multiple clips"""
    
    print("="*70)
    print(f"🎬 EXTENDED VIDEO GENERATION ({num_clips} clips)")
    print("="*70)
    print(f"Topic: {topic}")
    print(f"Target duration: {num_clips * 8} seconds")
    print("="*70)
    print()
    
    # Select random prompts
    selected_prompts = random.sample(hr_prompts, min(num_clips, len(hr_prompts)))
    while len(selected_prompts) < num_clips:
        selected_prompts.append(random.choice(hr_prompts))
    
    # Generate clips in parallel
    print("🚀 Starting parallel generation...")
    clip_paths = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_clips) as executor:
        futures = [
            executor.submit(generate_single_clip, prompt, i)
            for i, prompt in enumerate(selected_prompts)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            path = future.result()
            if path:
                clip_paths.append(path)
    
    if not clip_paths:
        print("❌ No clips generated!")
        return None
    
    print(f"\n✅ Generated {len(clip_paths)} clips")
    
    # Load and process clips
    print("🎥 Processing clips...")
    clips = []
    for path in sorted(clip_paths):
        c = VideoFileClip(path)
        # Resize to 9:16
        c = c.resize(height=h)
        if c.w < w:
            c = c.resize(width=w)
        c = c.crop(x1=c.w/2 - w/2, x2=c.w/2 + w/2, y1=0, y2=h)
        clips.append(c)
    
    # Concatenate
    main_video = concatenate_videoclips(clips, method="compose")
    total_duration = main_video.duration
    
    # Random logo
    logos = [os.path.join(PNG_DIR, f) for f in os.listdir(PNG_DIR) if f.endswith('.png')]
    selected_logo = random.choice(logos) if logos else None
    
    # Logo overlay
    if selected_logo and os.path.exists(selected_logo):
        logo_img = Image.open(selected_logo).convert('RGB')
        logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
        logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(total_duration)
    else:
        logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=total_duration).set_opacity(0)
    
    # Subtitles
    print("📝 Adding subtitles...")
    subtitle_clips = []
    
    # Subtitle every 8 seconds
    for i in range(len(clips)):
        start_time = i * 8 + 1
        if start_time < total_duration:
            sub = TextClip(
                f"{topic} - Part {i+1}",
                fontsize=60,
                color='#FFD700',
                font=FONT_BOLD,
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(w-100, None),
                align='center'
            ).set_position(('center', h - 400)).set_start(start_time).set_duration(2)
            subtitle_clips.append(sub)
    
    # Composite
    main_body = CompositeVideoClip([main_video, logo_overlay] + subtitle_clips).set_duration(total_duration)
    
    # Intro
    print("🎬 Adding intro/outro...")
    intro_duration = 1.5
    intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
    
    if selected_logo and os.path.exists(selected_logo):
        intro_logo_img = Image.open(selected_logo).convert('RGB')
        intro_logo = ImageClip(np.array(intro_logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
    else:
        intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)
    
    intro_text = TextClip(topic.upper(), fontsize=70, color='#000000', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
    intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])
    
    # Outro
    outro_duration = 3.5
    outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)
    
    if selected_logo and os.path.exists(selected_logo):
        outro_logo_img = Image.open(selected_logo).convert('RGB')
        outro_logo = ImageClip(np.array(outro_logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
    else:
        outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)
    
    outro_text = TextClip("VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color='#FFFFFF', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 300)).set_duration(outro_duration)
    outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])
    
    # Final video
    final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])
    
    # Output
    output_filename = f"extended_branded_{int(time.time())}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print("🎥 Rendering final video...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        bitrate="8000k",
        preset='medium',
        threads=4,
        logger=None,
        ffmpeg_params=[
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart'
        ]
    )
    
    print()
    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"📁 File: {output_path}")
    print(f"📋 Filename: {output_filename}")
    print(f"⏱️  Duration: {int(final_video.duration)}s")
    print(f"🌐 URL: https://vjgu.online/videos/videos/{output_filename}")
    print("="*70)
    
    return output_path, output_filename

if __name__ == "__main__":
    # Generate 3-clip video (24 seconds + intro/outro = ~29 seconds)
    create_extended_video(num_clips=3, topic="HR Career Success")
