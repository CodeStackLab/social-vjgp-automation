"""
AI-Generated Social Media Images with Branding
Step 1: Generate professional image with Vertex AI Imagen
Step 2: Add branding (logo, text, contact)
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
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import textwrap

# Configuration
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
OUTPUT_DIR = "/app/generated_media/images"
ASSETS_DIR = "/app/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "logo")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"
FONT_REGULAR = "/app/assets/fonts/Montserrat-Regular.ttf"

# Brand colors
BRAND_ORANGE = "#FF8D1F"
BRAND_BLACK = "#000000"
BRAND_WHITE = "#FFFFFF"

# HR-themed prompts for Imagen
HR_IMAGE_PROMPTS = [
    "Professional business woman in modern office, confident smile, business casual attire, natural lighting, photorealistic, high quality",
    "Corporate office meeting room, diverse professionals collaborating, modern workspace, glass walls, natural light, photorealistic",
    "Professional handshake in office, business meeting, corporate setting, professional attire, warm lighting, photorealistic",
    "Modern office workspace with laptop and documents, clean desk, professional environment, natural light, photorealistic",
    "Career coach mentoring session, professional office, two people discussing, modern interior, photorealistic",
    "Professional woman presenting in conference room, confident speaker, modern office, business attire, photorealistic",
    "Job interview scene, professional setting, office interior, business attire, natural lighting, photorealistic",
    "Professional team collaboration, modern office, diverse group, working together, natural light, photorealistic"
]

def initialize_vertex_ai():
    """Initialize Vertex AI"""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_ai_background(topic="professional office"):
    """
    Generate professional HR image using Vertex AI Imagen
    """
    try:
        print(f"🎨 Generating AI background image...")
        
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        # Select random HR prompt
        prompt = random.choice(HR_IMAGE_PROMPTS)
        
        print(f"   Prompt: {prompt[:60]}...")
        
        response = model.generate_images(
            prompt=f"{prompt}, 1080x1080, square format, professional photography",
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )
        
        if response and hasattr(response, 'images') and len(response.images) > 0:
            from io import BytesIO
            img = Image.open(BytesIO(response.images[0]._image_bytes))
            
            # Ensure 1080x1080
            if img.size != (1080, 1080):
                img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
            
            print(f"✅ AI image generated: {img.size}")
            return img
        
        print("❌ No images in response")
        return None
        
    except Exception as e:
        print(f"❌ AI generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_branding_to_image(
    base_image,
    title,
    subtitle=None,
    client_details=None,
    logo_size="small"  # small, medium, large
):
    """
    Add branding elements to AI-generated image
    - Small logo in corner
    - Text overlays with semi-transparent background
    - Contact footer
    """
    print(f"🎨 Adding branding to image...")
    
    img = base_image.copy()
    width, height = img.size
    
    # Add semi-transparent overlay for text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Dark gradient at bottom for text
    gradient_height = 500
    for y in range(gradient_height):
        alpha = int(180 * (y / gradient_height))
        overlay_draw.rectangle(
            [(0, height - gradient_height + y), (width, height - gradient_height + y + 1)],
            fill=(0, 0, 0, alpha)
        )
    
    # Composite overlay
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 95)
        font_subtitle = ImageFont.truetype(FONT_REGULAR, 42)
        font_contact = ImageFont.truetype(FONT_REGULAR, 30)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_contact = font_title
    
    # Add small logo in corner
    logo_sizes = {"small": 100, "medium": 140, "large": 180}
    logo_px = logo_sizes.get(logo_size, 100)
    
    logos = [f for f in os.listdir(PNG_DIR) if f.endswith('.png')] if os.path.exists(PNG_DIR) else []
    if logos:
        try:
            logo_path = os.path.join(PNG_DIR, random.choice(logos))
            logo = Image.open(logo_path).convert("RGBA")
            
            # Create white rounded background for logo
            logo_bg_size = logo_px + 30
            logo_bg = Image.new('RGBA', (logo_bg_size, logo_bg_size), (255, 255, 255, 0))
            logo_bg_draw = ImageDraw.Draw(logo_bg)
            logo_bg_draw.rounded_rectangle(
                [(0, 0), (logo_bg_size, logo_bg_size)],
                radius=20,
                fill=(255, 255, 255, 255)
            )
            
            # Resize and paste logo
            logo = logo.resize((logo_px, logo_px), Image.Resampling.LANCZOS)
            logo_bg.paste(logo, (15, 15), logo)
            
            # Paste on main image (top-left corner)
            img_rgba = img.convert('RGBA')
            img_rgba.paste(logo_bg, (40, 40), logo_bg)
            img = img_rgba.convert('RGB')
            draw = ImageDraw.Draw(img)
            
            print(f"✅ Logo added ({logo_size})")
        except Exception as e:
            print(f"Logo error: {e}")
    
    # Draw title at bottom (over gradient)
    y_offset = height - 400
    
    title_lines = textwrap.wrap(title.upper(), width=14)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        
        # Draw shadow
        draw.text((x + 3, y_offset + 3), line, font=font_title, fill=hex_to_rgb(BRAND_BLACK))
        
        # Draw main text (white)
        draw.text((x, y_offset), line, font=font_title, fill=hex_to_rgb(BRAND_WHITE))
        y_offset += text_height + 15
    
    # Draw subtitle
    if subtitle:
        y_offset += 20
        subtitle_lines = textwrap.wrap(subtitle, width=35)
        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=font_subtitle)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, font=font_subtitle, fill=hex_to_rgb(BRAND_WHITE))
            y_offset += 50
    
    # Add contact footer
    if client_details and client_details.get('contact_info'):
        footer_height = 90
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
            contact_items.append(f"{contact['phone']}")
        if contact.get('email'):
            contact_items.append(f"{contact['email']}")
        if contact.get('website'):
            contact_items.append(f"{contact['website']}")
        
        # Draw contact info
        contact_y = footer_y + 12
        for item in contact_items:
            bbox = draw.textbbox((0, 0), item, font=font_contact)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, contact_y), item, font=font_contact, fill=hex_to_rgb(BRAND_WHITE))
            contact_y += 26
        
        print(f"✅ Contact footer added")
    
    return img

def generate_ai_branded_post(
    topic,
    subtitle=None,
    client_details=None,
    platform="instagram",
    logo_size="small"
):
    """
    Complete workflow:
    1. Generate AI image with Vertex AI Imagen
    2. Add branding (logo, text, contact)
    """
    print("="*70)
    print(f"🎨 AI-GENERATED BRANDED POST - {platform.upper()}")
    print("="*70)
    print(f"Topic: {topic}")
    print("="*70)
    print()
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Step 1: Generate AI background
    print("STEP 1: Generating AI background image...")
    ai_image = generate_ai_background(topic)
    
    if not ai_image:
        print("❌ Failed to generate AI image")
        return None
    
    print()
    
    # Step 2: Add branding
    print("STEP 2: Adding branding elements...")
    branded_image = add_branding_to_image(
        base_image=ai_image,
        title=topic,
        subtitle=subtitle,
        client_details=client_details,
        logo_size=logo_size
    )
    
    # Save image
    timestamp = int(time.time())
    filename = f"{platform}_ai_branded_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    branded_image.save(output_path, quality=95, optimize=True)
    
    print()
    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"📁 File: {output_path}")
    print(f"📋 Filename: {filename}")
    print(f"📐 Size: {branded_image.size}")
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
    
    print("✅ AI-generated branded post generator loaded. Ready to use.")
