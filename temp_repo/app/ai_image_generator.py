"""
AI-Enhanced Image Post Generator
Supports both branded and AI-generated backgrounds for variety
"""

import os
import random
import time
import textwrap
import json
import base64
import numpy as np
from io import BytesIO
import PIL.Image
from moviepy.editor import *
import moviepy.video.fx.all as vfx
from google.cloud import aiplatform, texttospeech
from platform_optimizer import PLATFORM_SPECS
from google.oauth2 import service_account
from vertexai.preview.vision_models import ImageGenerationModel

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from google.cloud import speech
except ImportError:
    speech = None

# Configuration
ASSETS_DIR = "/app/assets"
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
OUTPUT_DIR = "/app/generated_media"

FONT_BOLD = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
LOGO_ICON = os.path.join(ASSETS_DIR, "logo/logo.png")

DIRS = {
    "video": os.path.join(OUTPUT_DIR, "videos"),
    "image": os.path.join(OUTPUT_DIR, "images"),
    "temp": os.path.join(OUTPUT_DIR, "temp")
}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# HR-Themed Prompt Library for AI Backgrounds
HR_BACKGROUND_PROMPTS = [
    # Office & Workspace
    "Modern minimalist office desk with laptop and notebook, bright natural light, professional clean background, 4k, vertical composition",
    "Corporate meeting room with glass walls, modern furniture, professional atmosphere, 9:16 aspect",
    "Co-working space with plants and natural light, professional collaborative environment, bright, vertical",
    
    # Career Growth
    "Upward trending arrow graphic on professional background, success concept, gradient blue, vertical",
    "Staircase leading upward, career advancement metaphor, motivational professional setting, 9:16",
    "Mountain peak with success flag, achievement concept, inspirational gradient background, vertical",
    
    # Job Search & Interviews
    "Resume document on clean modern desk with coffee cup, job application concept, professional, vertical",
    "Professional job interview chairs, corporate office background, natural light, 9:16 composition",
    "Laptop showing career dashboard, coffee beside it, home office setup, professional lighting, vertical",
    
    # Skills & Training
    "Stack of professional books with coffee, learning development, bright clean background, vertical",
    "Certificate of achievement on desk, professional development concept, minimalist, 9:16",
    "Online training on laptop screen, skill development, modern home office, vertical composition",
    
    # Teamwork & Success  
    "Business professionals collaborating, modern office, teamwork concept, professional, vertical",
    "Handshake in modern corporate setting, partnership success, professional lighting, 9:16",
    "Team celebrating success, modern office environment, professional achievement, vertical"
]


def generate_hr_background(w=1080, h=1920, aspect_ratio="9:16"):
    """
    Generate HR/career themed background using Vertex AI Imagen
    Returns PIL Image object
    """
    try:
        # Select random HR prompt
        prompt = random.choice(HR_BACKGROUND_PROMPTS)
        
        print(f"🎨 Generating AI background: {prompt[:60]}...")
        
        # Load Imagen model (updated to latest version)
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        # Generate image
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            add_watermark=False,
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )
        
        # Convert to PIL Image
        image_bytes = response.images[0]._image_bytes
        bg_image = PIL.Image.open(BytesIO(image_bytes))
        
        # Resize to exact dimensions
        bg_image = bg_image.resize((w, h), PIL.Image.LANCZOS)
        
        print("✅ AI background generated successfully")
        return bg_image
        
    except Exception as e:
        print(f"⚠️ AI generation failed: {e}, using fallback")
        # Fallback to gradient background
        bg = PIL.Image.new('RGB', (w, h), (45, 55, 72))  # Professional dark blue
        return bg


def create_ai_image_post(title, caption, use_ai_background=True, show_logo=True, platform='instagram'):
    """
    Creates image posts with AI-generated backgrounds or branded style
    
    Args:
        title: Main heading
        caption: Body text  
        use_ai_background: True for AI, False for branded
        show_logo: Whether to show VirtualJobGuru logo
        platform: Target platform for sizing
        
    Returns:
        (image_path, filename) or (None, error)
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Resolve dimensions from platform specs
        spec = PLATFORM_SPECS.get(platform.lower(), PLATFORM_SPECS['instagram'])
        w, h = spec['width'], spec['height']
        aspect_ratio = spec['aspect_ratio']
        
        print(f"🎨 Creating image: AI_BG={use_ai_background}, Logo={show_logo}")
        
        # GENERATE BACKGROUND
        if use_ai_background:
            bg_pil = generate_hr_background(w, h, aspect_ratio=aspect_ratio)
            # Add slight dark overlay for text readability
            overlay = PIL.Image.new('RGBA', (w, h), (0, 0, 0, 100))
            bg_pil = PIL.Image.alpha_composite(bg_pil.convert('RGBA'), overlay).convert('RGB')
        else:
            # Branded gradient background
            bg_pil = PIL.Image.new('RGB', (w, h), (255, 141, 31))  # Orange
        
        draw = ImageDraw.Draw(bg_pil)
        
        # LOAD FONTS
        try:
            title_font = ImageFont.truetype(FONT_BOLD, 110)
            caption_font = ImageFont.truetype(FONT_BOLD, 55)
        except:
            title_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()
        
        # TEXT STYLING based on background
        if use_ai_background:
            title_color = (255, 255, 255)  # White
            caption_color = (240, 240, 240)  # Light gray
            # Add text shadow for AI backgrounds
            shadow_offset = 3
        else:
            title_color = (0, 0, 0)  # Black on branded
            caption_color = (50, 50, 50)  # Dark gray
            shadow_offset = 0
        
        # DRAW TITLE (centered, top third)
        title_wrapped = textwrap.wrap(title.upper(), width=15)
        title_text = "\n".join(title_wrapped)
        
        title_y = h // 4
        for line in title_wrapped:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = bbox[2] - bbox[0]
            x = (w - line_width) // 2
            
            # Shadow if AI background
            if shadow_offset:
                draw.text((x + shadow_offset, title_y + shadow_offset), line, font=title_font, fill=(0, 0, 0))
            
            draw.text((x, title_y), line, font=title_font, fill=title_color)
            title_y += bbox[3] - bbox[1] + 20
        
        # DRAW CAPTION (centered, middle)
        caption_wrapped = textwrap.wrap(caption, width=30)
        caption_y = h // 2 + 100
        
        for line in caption_wrapped:
            bbox = draw.textbbox((0, 0), line, font=caption_font)
            line_width = bbox[2] - bbox[0]
            x = (w - line_width) // 2
            
            if shadow_offset:
                draw.text((x + shadow_offset, caption_y + shadow_offset), line, font=caption_font, fill=(0, 0, 0))
            
            draw.text((x, caption_y), line, font=caption_font, fill=caption_color)
            caption_y += bbox[3] - bbox[1] + 15
        
        # ADD LOGO (if enabled)
        if show_logo and os.path.exists(LOGO_ICON):
            logo = PIL.Image.open(LOGO_ICON).convert('RGBA')
            logo = logo.resize((250, int(250 * logo.height / logo.width)), PIL.Image.LANCZOS)
            
            # Position logo (top-right)
            logo_x = w - logo.width - 60
            logo_y = 60
            
            bg_pil.paste(logo, (logo_x, logo_y), logo)
        
        # SAVE
        filename = f"ai_post_{int(time.time())}.png"
        output_path = os.path.join(DIRS["image"], filename)
        
        bg_pil.save(output_path, "PNG", quality=95)
        
        print(f"✅ Image created: {output_path}")
        return output_path, filename
        
    except Exception as e:
        import traceback
        print(f"❌ Image creation error: {e}\n{traceback.format_exc()}")
        return None, str(e)
