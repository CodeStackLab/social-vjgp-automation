"""
Professional Social Media Image Generator - FIXED VERSION
Matches VirtualJobGuru samples EXACTLY
"""

import os
import sys
import time
import random
sys.path.insert(0, '/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'

from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Configuration
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
OUTPUT_DIR = "/app/generated_media/images"
ASSETS_DIR = "/app/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"
FONT_REGULAR = "/app/assets/fonts/Montserrat-Regular.ttf"

# Brand colors
BRAND_ORANGE = "#FF8D1F"
BRAND_BLACK = "#000000"
BRAND_WHITE = "#FFFFFF"

def initialize_vertex_ai():
    """Initialize Vertex AI"""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_professional_social_post(
    title,
    subtitle=None,
    background_type="solid",  # solid, gradient, photo
    client_details=None,
    platform="instagram"
):
    """
    Create professional post matching exact VirtualJobGuru style
    """
    print(f"🎨 Creating professional {platform} post...")
    
    # Canvas size
    width, height = 1080, 1080
    
    # Create base image
    if background_type == "gradient":
        # Orange gradient background
        img = Image.new('RGB', (width, height), hex_to_rgb(BRAND_ORANGE))
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect (darker at bottom)
        for y in range(height):
            alpha = int(255 * (y / height) * 0.3)
            draw.rectangle([(0, y), (width, y+1)], fill=(0, 0, 0, alpha))
    else:
        # Solid orange background
        img = Image.new('RGB', (width, height), hex_to_rgb(BRAND_ORANGE))
    
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 110)  # Larger title
        font_subtitle = ImageFont.truetype(FONT_REGULAR, 45)
        font_contact = ImageFont.truetype(FONT_REGULAR, 32)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_contact = font_title
    
    # Add logo (top-left with white background)
    logos = [f for f in os.listdir(PNG_DIR) if f.endswith('.png')] if os.path.exists(PNG_DIR) else []
    if logos:
        try:
            logo_path = os.path.join(PNG_DIR, random.choice(logos))
            logo = Image.open(logo_path).convert("RGBA")
            
            # Create white rounded square background
            logo_bg_size = 180
            logo_bg = Image.new('RGBA', (logo_bg_size, logo_bg_size), (255, 255, 255, 255))
            draw_logo_bg = ImageDraw.Draw(logo_bg)
            draw_logo_bg.rounded_rectangle(
                [(0, 0), (logo_bg_size, logo_bg_size)],
                radius=25,
                fill=(255, 255, 255, 255)
            )
            
            # Resize and paste logo
            logo = logo.resize((140, 140), Image.Resampling.LANCZOS)
            logo_bg.paste(logo, (20, 20), logo)
            
            # Paste on main image
            img_rgba = img.convert('RGBA')
            img_rgba.paste(logo_bg, (60, 60), logo_bg)
            img = img_rgba.convert('RGB')
            draw = ImageDraw.Draw(img)
        except Exception as e:
            print(f"Logo error: {e}")
    
    # Draw title (center, large, bold, white)
    y_offset = 350
    
    title_lines = textwrap.wrap(title.upper(), width=12)
    for line in title_lines:
        # Measure text
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        
        # Draw shadow
        shadow_offset = 5
        draw.text((x + shadow_offset, y_offset + shadow_offset), line, font=font_title, fill=hex_to_rgb(BRAND_BLACK))
        
        # Draw main text
        draw.text((x, y_offset), line, font=font_title, fill=hex_to_rgb(BRAND_WHITE))
        y_offset += text_height + 20
    
    # Draw subtitle if provided
    if subtitle:
        y_offset += 30
        subtitle_lines = textwrap.wrap(subtitle, width=30)
        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=font_subtitle)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, font=font_subtitle, fill=hex_to_rgb(BRAND_WHITE))
            y_offset += 55
    
    # Add contact footer (black bar at bottom)
    if client_details and client_details.get('contact_info'):
        footer_height = 100
        footer_y = height - footer_height
        
        # Black footer
        draw.rectangle(
            [(0, footer_y), (width, height)],
            fill=hex_to_rgb(BRAND_BLACK)
        )
        
        contact = client_details['contact_info']
        
        # Contact items
        contact_items = []
        if contact.get('phone'):
            contact_items.append(f"  {contact['phone']}")
        if contact.get('email'):
            contact_items.append(f"  {contact['email']}")
        if contact.get('website'):
            contact_items.append(f"  {contact['website']}")
        
        # Draw contact info
        contact_y = footer_y + 15
        for item in contact_items:
            bbox = draw.textbbox((0, 0), item, font=font_contact)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, contact_y), item, font=font_contact, fill=hex_to_rgb(BRAND_WHITE))
            contact_y += 28
    
    return img

def generate_social_post_v2(
    topic,
    subtitle=None,
    client_details=None,
    platform="instagram"
):
    """
    Generate professional social post - FIXED VERSION
    """
    print("="*70)
    print(f"🎨 PROFESSIONAL SOCIAL POST V2 - {platform.upper()}")
    print("="*70)
    print(f"Topic: {topic}")
    print("="*70)
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Create post
    img = create_professional_social_post(
        title=topic,
        subtitle=subtitle,
        background_type="solid",
        client_details=client_details,
        platform=platform
    )
    
    # Save image
    timestamp = int(time.time())
    filename = f"{platform}_post_v2_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    img.save(output_path, quality=95, optimize=True)
    
    print()
    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"📁 File: {output_path}")
    print(f"📋 Filename: {filename}")
    print(f"📐 Size: {img.size}")
    print(f"🌐 URL: https://vjgu.online/videos/images/{filename}")
    print("="*70)
    
    return output_path

# Example usage
if __name__ == "__main__":
    client_details = {
        "contact_info": {
            "website": "www.virtualjobguru.com",
            "email": "info@virtualjobguru.com",
            "phone": "+49 1577 4331858"
        }
    }
    
    print("✅ Professional social post generator V2 loaded. Ready to use.")
