import os
import time
from moviepy.editor import *
import numpy as np
from PIL import Image
# Monkeypatch ANTIALIAS for newer Pillow versions
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import *
import numpy as np
BASE_DIR = "/root/.gemini/antigravity/scratch/social_automato/app"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_media")
DIRS = {
    "video": os.path.join(OUTPUT_DIR, "temp/videos"),
    "temp": os.path.join(OUTPUT_DIR, "temp")
}
LOGO_ICON = os.path.join(ASSETS_DIR, "logo.png")
FONT_BOLD = "Montserrat-Bold" # Assuming installed or available
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PRIMARY_ORANGE = (255, 141, 31)

def assemble_branded(clip_path):
    print(f"Processing clip: {clip_path}")
    
    # 1. Load Clip
    clip = VideoFileClip(clip_path)
    w, h = 1080, 1920 # 9:16 target
    
    # Resize/Crop
    clip = clip.resize(height=h)
    if clip.w < w:
        clip = clip.resize(width=w)
    clip = clip.crop(x1=clip.w/2 - w/2, x2=clip.w/2 + w/2, y1=0, y2=h)
    
    # Force 8s (or clip duration if less)
    total_duration = min(clip.duration, 8)
    clip = clip.set_duration(total_duration)
    
    # 2. Intro Scene
    intro_duration = 1.5
    intro_bg = ColorClip(size=(w, h), color=PRIMARY_ORANGE, duration=intro_duration)
    
    if os.path.exists(LOGO_ICON):
        logo_img = Image.open(LOGO_ICON).convert('RGB')
        intro_logo = ImageClip(np.array(logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
    else:
        intro_logo = ColorClip(size=(1, 1), color=(0,0,0), duration=intro_duration)
        
    intro_text = TextClip("Job & Career Tips".upper(), fontsize=70, color='black', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
    intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])

    # 3. Outro Scene
    outro_duration = 3.5
    outro_bg = ColorClip(size=(w, h), color=BLACK, duration=outro_duration)
    outro_text = TextClip("VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color='white', font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 300)).set_duration(outro_duration)
    
    if os.path.exists(LOGO_ICON):
        outro_logo = ImageClip(np.array(logo_img)).resize(width=400).set_position('center').set_duration(outro_duration)
        outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])
    else:
        outro_composite = CompositeVideoClip([outro_bg, outro_text])

    # 4. Main Body with Overlay
    # Logo Overlay
    if os.path.exists(LOGO_ICON):
        logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9).set_position((w - 200, 60)).set_duration(total_duration)
        main_body = CompositeVideoClip([clip, logo_overlay])
    else:
        main_body = clip

    # 5. Concatenate
    final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])
    
    # 6. Write
    filename = f"branded_8s_assembled_{int(time.time())}.mp4"
    output_path = os.path.join(DIRS["video"], filename)
    
    final_video.write_videofile(
        output_path, 
        fps=30, 
        bitrate="8000k",
        threads=4,
        preset='medium'
    )
    
    return output_path, filename

if __name__ == "__main__":
    clip_path = "/root/.gemini/antigravity/scratch/social_automato/app/generated_media/temp/gen_clip_1770480532786.mp4"
    p, f = assemble_branded(clip_path)
    print(f"SUCCESS: {p}")
