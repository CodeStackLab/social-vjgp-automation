"""
Professional Social Media Image Generator
Creates images matching VirtualJobGuru brand style
Supports: Instagram, Facebook, LinkedIn, Twitter
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

# Social media sizes
SOCIAL_SIZES = {
    "instagram": (1080, 1080),  # Square
    "facebook": (1080, 1080),   # Square
    "linkedin": (1080, 1080),   # Square
    "twitter": (1080, 1080)     # Square
}

def initialize_vertex_ai():
    """Initialize Vertex AI"""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

def generate_background_image(prompt="professional office background"):
    """Generate background image using Vertex AI Imagen"""
    try:
        print(f"🎨 Generating background...")
        
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        response = model.generate_images(
            prompt=f"{prompt}, photorealistic, high quality, professional, clean, modern",
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )
        
        if response and hasattr(response, 'images') and len(response.images) > 0:
            from io import BytesIO
            img = Image.open(BytesIO(response.images[0]._image_bytes))
            # Resize to 1080x1080
            img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
            print(f"✅ Background generated")
            return img
        
        return None
        
    except Exception as e:
        print(f"❌ Background generation error: {e}")
        return None

def create_professional_post(
    title,
    subtitle=None,
    key_points=None,
    background_image=None,
    background_color=None,
    client_details=None,
    platform="instagram"
):
    """
    Create professional social media post matching VirtualJobGuru style
    
    Args:
        title: Main headline text
        subtitle: Optional subtitle
        key_points: List of key points (max 4)
        background_image: PIL Image for background (optional)
        background_color: Background color if no image (default: orange)
        client_details: Client contact info
        platform: Social media platform
        
    Returns:
        PIL Image
    """
    print(f"🎨 Creating professional post for {platform}...")
    
    # Get size for platform
    width, height = SOCIAL_SIZES.get(platform, (1080, 1080))
    
    # Create base image
    if background_image:
        # Use provided background
        img = background_image.copy()
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Add semi-transparent overlay for text readability
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
    else:
        # Solid color background
        bg_color = background_color or BRAND_ORANGE
        img = Image.new('RGB', (width, height), bg_color)
    
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 90)
        font_subtitle = ImageFont.truetype(FONT_BOLD, 50)
        font_points = ImageFont.truetype(FONT_REGULAR, 38)
        font_contact = ImageFont.truetype(FONT_REGULAR, 28)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_points = font_title
        font_contact = font_title
    
    # Draw title (top section)
    y_offset = 80
    
    # Wrap title text
    title_lines = textwrap.wrap(title.upper(), width=15)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        
        # Draw text with slight shadow
        draw.text((x+3, y_offset+3), line, font=font_title, fill=BRAND_BLACK)
        draw.text((x, y_offset), line, font=font_title, fill=BRAND_WHITE)
        y_offset += 100
    
    # Draw subtitle if provided
    if subtitle:
        y_offset += 20
        subtitle_lines = textwrap.wrap(subtitle, width=25)
        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=font_subtitle)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, font=font_subtitle, fill=BRAND_WHITE)
            y_offset += 60
    
    # Draw key points if provided
    if key_points and len(key_points) > 0:
        y_offset += 40
        
        for point in key_points[:4]:  # Max 4 points
            # Draw point box
            box_height = 100
            box_margin = 80
            
            # Black rounded rectangle
            draw.rounded_rectangle(
                [(box_margin, y_offset), (width - box_margin, y_offset + box_height)],
                radius=15,
                fill=BRAND_BLACK
            )
            
            # Point text
            point_lines = textwrap.wrap(point, width=40)
            text_y = y_offset + 15
            for line in point_lines:
                bbox = draw.textbbox((0, 0), line, font=font_points)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, text_y), line, font=font_points, fill=BRAND_WHITE)
                text_y += 45
            
            y_offset += box_height + 20
    
    # Add logo (top-left corner)
    logos = [os.path.join(PNG_DIR, f) for f in os.listdir(PNG_DIR) if f.endswith('.png')]
    if logos:
        try:
            logo_path = random.choice(logos)
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((120, 120), Image.Resampling.LANCZOS)
            
            # White rounded background for logo
            logo_bg = Image.new('RGBA', (140, 140), (255, 255, 255, 255))
            draw_logo = ImageDraw.Draw(logo_bg)
            draw_logo.rounded_rectangle([(0, 0), (140, 140)], radius=20, fill=(255, 255, 255, 255))
            
            # Paste logo on background
            logo_bg.paste(logo, (10, 10), logo)
            
            # Paste on main image
            img_rgba = img.convert('RGBA')
            img_rgba.paste(logo_bg, (60, 60), logo_bg)
            img = img_rgba.convert('RGB')
        except Exception as e:
            print(f"Logo error: {e}")
    
    # Add contact footer (black bar at bottom)
    if client_details and client_details.get('contact_info'):
        footer_height = 100
        footer_y = height - footer_height
        
        # Black footer background
        draw.rectangle(
            [(0, footer_y), (width, height)],
            fill=BRAND_BLACK
        )
        
        contact = client_details['contact_info']
        
        # Contact info in footer
        contact_items = []
        if contact.get('phone'):
            contact_items.append(f"  {contact['phone']}")
        if contact.get('email'):
            contact_items.append(f"  {contact['email']}")
        if contact.get('website'):
            contact_items.append(f"  {contact['website']}")
        
        # Draw contact items
        contact_y = footer_y + 20
        for item in contact_items:
            bbox = draw.textbbox((0, 0), item, font=font_contact)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, contact_y), item, font=font_contact, fill=BRAND_WHITE)
            contact_y += 35
    
    return img

def generate_social_post(
    topic,
    research_data=None,
    client_details=None,
    platform="instagram",
    use_ai_background=True
):
    """
    Generate complete social media post
    
    Args:
        topic: Post topic/title
        research_data: Research insights (optional)
        client_details: Client details
        platform: Social platform
        use_ai_background: Whether to generate AI background
        
    Returns:
        Path to generated image
    """
    print("="*70)
    print(f"🎨 PROFESSIONAL SOCIAL POST - {platform.upper()}")
    print("="*70)
    print(f"Topic: {topic}")
    print("="*70)
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Generate background if requested
    background = None
    if use_ai_background and random.random() < 0.5:  # 50% chance
        bg_prompts = [
            "modern office interior, professional workspace",
            "business meeting room, corporate setting",
            "professional desk with laptop, clean workspace",
            "modern corporate office, glass walls and plants"
        ]
        background = generate_background_image(random.choice(bg_prompts))
    
    # Extract key points from research
    key_points = []
    if research_data and research_data.get('research'):
        # Simple extraction - in real use, parse research better
        research_text = research_data['research']
        # For now, use generic points
        key_points = [
            "Professional guidance for career success",
            "Expert HR insights and strategies",
            "Proven methods for job seekers"
        ]
    
    # Create post
    img = create_professional_post(
        title=topic,
        subtitle=None,
        key_points=key_points if len(key_points) > 0 else None,
        background_image=background,
        background_color=BRAND_ORANGE if not background else None,
        client_details=client_details,
        platform=platform
    )
    
    # Save image
    timestamp = int(time.time())
    filename = f"{platform}_post_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    img.save(output_path, quality=95)
    
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
    
    print("✅ Professional social post generator loaded. Ready to use.")
