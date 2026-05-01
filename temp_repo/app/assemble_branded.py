#!/usr/bin/env python3
"""
Generate branded video using existing clips
"""

import sys
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import os
from moviepy.editor import *
import numpy as np
from PIL import Image

# Paths
TEMP_DIR = "/app/generated_media/temp"
OUTPUT_DIR = "/app/output/videos"
LOGO_ICON = "/app/assets/logo/logo.png"
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"

# Find the 4 generated clips
clip_files = sorted([
    os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) 
    if f.startswith("gen_clip_") and f.endswith(".mp4")
], key=os.path.getmtime, reverse=True)[:4]

print(f"Found {len(clip_files)} clips:")
for cf in clip_files:
    print(f"  - {cf}")

if len(clip_files) < 4:
    print("ERROR: Need 4 clips!")
    sys.exit(1)

w, h = 1080, 1920
total_duration = 32  # 4 clips x 8 seconds

print("\n🎬 Creating branded video...")

# Load clips
clips = []
for p in clip_files:
    c = VideoFileClip(p)
    # Resize to 9:16
    c = c.resize(height=h)
    if c.w < w:
        c = c.resize(width=w)
    c = c.crop(x1=c.w/2 - w/2, x2=c.w/2 + w/2, y1=0, y2=h)
    c = c.set_duration(8)
    clips.append(c)

# Concatenate
base_video = concatenate_videoclips(clips, method="compose")
base_video = base_video.set_duration(total_duration)

# Logo overlay
if os.path.exists(LOGO_ICON):
    logo_img = Image.open(LOGO_ICON).convert('RGB')
    logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
    logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(total_duration)
else:
    logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=total_duration).set_opacity(0)

# Intro
intro_duration = 1.5
intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
if os.path.exists(LOGO_ICON):
    intro_logo_img = Image.open(LOGO_ICON).convert('RGB')
    intro_logo = ImageClip(np.array(intro_logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
else:
    intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)
intro_text = TextClip("HR SUCCESS TIPS", fontsize=70, color='#000000', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])

# Outro
outro_duration = 3.5
outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)
if os.path.exists(LOGO_ICON):
    outro_logo_img = Image.open(LOGO_ICON).convert('RGB')
    outro_logo = ImageClip(np.array(outro_logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
else:
    outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)
outro_text = TextClip("VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color='#FFFFFF', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 300)).set_duration(outro_duration)
outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])

# Main body with logo
main_body = CompositeVideoClip([base_video, logo_overlay]).set_duration(total_duration)

# Final video
final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])

# Output
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, f"branded_reel_{int(time.time())}.mp4")

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

print(f"\n✅ SUCCESS!")
print(f"📁 Video: {output_path}")
print(f"🌐 URL: https://vjgu.online/videos/{os.path.basename(output_path)}")
