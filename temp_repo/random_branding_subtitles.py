#!/usr/bin/env python3
"""
Add random branding + subtitles to existing video
Uses random logo from assets folder
"""

import os
import time
import random
from moviepy.editor import *
import numpy as np
from PIL import Image

# Paths
VIDEO_PATH = "/app/generated_media/videos/veo3_single_test.mp4"
OUTPUT_DIR = "/app/generated_media/videos"
ASSETS_DIR = "/app/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"

# Colors
PRIMARY_ORANGE = "#FF8D1F"
BLACK = "#000000"
WHITE = "#FFFFFF"

w, h = 1080, 1920

print("="*70)
print("🎬 RANDOM BRANDING + SUBTITLES")
print("="*70)
print()

# Get random logo from assets
print("🎨 Selecting random logo...")
logos = []
if os.path.exists(PNG_DIR):
    for f in os.listdir(PNG_DIR):
        if f.lower().endswith('.png'):
            logos.append(os.path.join(PNG_DIR, f))

if logos:
    selected_logo = random.choice(logos)
    print(f"✅ Selected: {os.path.basename(selected_logo)}")
else:
    selected_logo = os.path.join(PNG_DIR, "virtualjobguru-01.png")
    print(f"⚠️  Using default logo")

# Load video
print("📹 Loading video...")
main_clip = VideoFileClip(VIDEO_PATH)

# Resize to 9:16
if main_clip.w != w or main_clip.h != h:
    main_clip = main_clip.resize(height=h)
    if main_clip.w < w:
        main_clip = main_clip.resize(width=w)
    main_clip = main_clip.crop(x1=main_clip.w/2 - w/2, x2=main_clip.w/2 + w/2, y1=0, y2=h)

main_duration = main_clip.duration

# Random logo position (top-left, top-right, bottom-left, bottom-right)
positions = [
    (50, 60),           # Top-left
    (w - 200, 60),      # Top-right
    (50, h - 200),      # Bottom-left
    (w - 200, h - 200)  # Bottom-right
]
logo_pos = random.choice(positions)

print(f"🎨 Logo position: {logo_pos}")

# Logo overlay
if os.path.exists(selected_logo):
    logo_img = Image.open(selected_logo).convert('RGB')
    logo_size = random.randint(120, 180)  # Random size
    logo_overlay = ImageClip(np.array(logo_img)).resize(width=logo_size).set_opacity(0.9)
    logo_overlay = logo_overlay.set_position(logo_pos).set_duration(main_duration)
else:
    logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=main_duration).set_opacity(0)

# Create subtitles (simulated - since we don't have audio transcription)
print("📝 Creating subtitles...")

# Sample subtitle text (you can customize this based on your content)
subtitle_texts = [
    "Professional HR Tips",
    "Career Growth Strategies",
    "Success in Your Career",
    "Expert Advice for You",
    "Your Path to Success"
]

selected_subtitle = random.choice(subtitle_texts)

# Create animated subtitle clips
subtitle_clips = []

# Subtitle 1: Appears at 1s, stays for 2s
sub1 = TextClip(
    selected_subtitle.upper(),
    fontsize=65,
    color='#FFD700',  # Gold
    font=FONT_BOLD,
    stroke_color='black',
    stroke_width=3,
    method='caption',
    size=(w-100, None),
    align='center'
).set_position(('center', h - 400)).set_start(1).set_duration(2)

subtitle_clips.append(sub1)

# Subtitle 2: Appears at 3.5s, stays for 2s
sub2 = TextClip(
    "VirtualJobGuru",
    fontsize=55,
    color=WHITE,
    font=FONT_BOLD,
    stroke_color=PRIMARY_ORANGE,
    stroke_width=2,
    method='caption',
    size=(w-100, None),
    align='center'
).set_position(('center', h - 350)).set_start(3.5).set_duration(2)

subtitle_clips.append(sub2)

# Subtitle 3: Appears at 6s, stays till end
sub3 = TextClip(
    "Follow for More Tips",
    fontsize=50,
    color=PRIMARY_ORANGE,
    font=FONT_BOLD,
    stroke_color='black',
    stroke_width=2,
    method='caption',
    size=(w-100, None),
    align='center'
).set_position(('center', h - 300)).set_start(6).set_duration(main_duration - 6)

subtitle_clips.append(sub3)

# Main body with logo and subtitles
print("🎥 Compositing...")
main_body = CompositeVideoClip([main_clip, logo_overlay] + subtitle_clips).set_duration(main_duration)

# Random intro color
intro_colors = [
    (255, 141, 31),  # Orange
    (0, 0, 0),       # Black
    (255, 255, 255), # White
    (15, 23, 42)     # Dark blue
]
intro_color = random.choice(intro_colors)
text_color = WHITE if intro_color != (255, 255, 255) else BLACK

print(f"🎨 Intro color: RGB{intro_color}")

# Intro scene
intro_duration = 1.5
intro_bg = ColorClip(size=(w, h), color=intro_color, duration=intro_duration)

if os.path.exists(selected_logo):
    intro_logo_img = Image.open(selected_logo).convert('RGB')
    intro_logo = ImageClip(np.array(intro_logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
else:
    intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)

intro_text = TextClip(
    "HR SUCCESS TIPS",
    fontsize=70,
    color=text_color,
    font=FONT_BOLD,
    size=(w-100, None),
    method='caption'
).set_position(('center', h/2 + 350)).set_duration(intro_duration)

intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])

# Outro scene
outro_duration = 3.5
outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)

if os.path.exists(selected_logo):
    outro_logo_img = Image.open(selected_logo).convert('RGB')
    outro_logo = ImageClip(np.array(outro_logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
else:
    outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)

outro_text = TextClip(
    "VirtualJobGuru\nYour Career. Your Growth.",
    fontsize=55,
    color=WHITE,
    font=FONT_BOLD,
    size=(w-100, None),
    method='caption'
).set_position(('center', h/2 + 300)).set_duration(outro_duration)

outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])

# Final video
print("🎬 Assembling final video...")
final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])

# Output with random filename
output_filename = f"branded_random_{int(time.time())}.mp4"
output_path = os.path.join(OUTPUT_DIR, output_filename)

print("🎥 Rendering...")
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
print(f"🎨 Logo: {os.path.basename(selected_logo)}")
print(f"📝 Subtitle: {selected_subtitle}")
print(f"🌐 URL: https://vjgu.online/videos/videos/{output_filename}")
print("="*70)
