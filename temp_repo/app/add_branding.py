#!/usr/bin/env python3
"""
Add branding to existing Veo 3 video
"""

import os
import time
from moviepy.editor import *
import numpy as np
from PIL import Image

# Paths
VIDEO_PATH = "/app/generated_media/videos/veo3_single_test.mp4"
OUTPUT_DIR = "/app/generated_media/videos"
LOGO_ICON = "/app/assets/logo/logo.png"
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"

# Colors
PRIMARY_ORANGE = "#FF8D1F"
BLACK = "#000000"
WHITE = "#FFFFFF"

w, h = 1080, 1920

print("="*70)
print("🎬 ADDING BRANDING TO EXISTING VIDEO")
print("="*70)
print(f"Input: {VIDEO_PATH}")
print("="*70)
print()

# Load existing video
print("📹 Loading video...")
main_clip = VideoFileClip(VIDEO_PATH)

# Resize to 9:16 if needed
if main_clip.w != w or main_clip.h != h:
    main_clip = main_clip.resize(height=h)
    if main_clip.w < w:
        main_clip = main_clip.resize(width=w)
    main_clip = main_clip.crop(x1=main_clip.w/2 - w/2, x2=main_clip.w/2 + w/2, y1=0, y2=h)

main_duration = main_clip.duration

# Logo overlay (top right)
print("🎨 Adding logo overlay...")
if os.path.exists(LOGO_ICON):
    logo_img = Image.open(LOGO_ICON).convert('RGB')
    logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
    logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(main_duration)
else:
    logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=main_duration).set_opacity(0)

# Main body with logo
main_body = CompositeVideoClip([main_clip, logo_overlay]).set_duration(main_duration)

# Intro scene
print("🎬 Creating intro...")
intro_duration = 1.5
intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)  # Orange

if os.path.exists(LOGO_ICON):
    intro_logo_img = Image.open(LOGO_ICON).convert('RGB')
    intro_logo = ImageClip(np.array(intro_logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
else:
    intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)

intro_text = TextClip("HR SUCCESS TIPS", fontsize=70, color=BLACK, font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])

# Outro scene
print("🎬 Creating outro...")
outro_duration = 3.5
outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)  # Black

if os.path.exists(LOGO_ICON):
    outro_logo_img = Image.open(LOGO_ICON).convert('RGB')
    outro_logo = ImageClip(np.array(outro_logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
else:
    outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)

outro_text = TextClip("VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color=WHITE, font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 300)).set_duration(outro_duration)
outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])

# Final video: Intro + Main + Outro
print("🎥 Assembling final video...")
final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])

# Output
output_filename = f"branded_veo3_{int(time.time())}.mp4"
output_path = os.path.join(OUTPUT_DIR, output_filename)

print("🎬 Rendering...")
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
print(f"🌐 URL: https://vjgu.online/videos/videos/{output_filename}")
print("="*70)
