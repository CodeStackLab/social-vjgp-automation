"""
Image Post Generator with Vertex AI Imagen
Generates professional HR-themed images with branding and text overlays
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
PNG_DIR = os.path.join(ASSETS_DIR, "logo")
FONT_BOLD = "/app/assets/fonts/Montserrat-Bold.ttf"
FONT_REGULAR = "/app/assets/fonts/Montserrat-Regular.ttf"

# Brand colors
BRAND_COLORS = {
    "primary_orange": "#FF8D1F",
    "black": "#000000",
    "white": "#FFFFFF",
    "dark_blue": "#0F172A",
    "gold": "#FFD700"
}

# HR-themed prompts
HR_PROMPTS = [
    "Professional HR consultant in modern office, confident pose, business attire, natural lighting, photorealistic",
    "Job interview scene, professional setting, two people shaking hands, corporate office background, realistic",
    "Career success concept, professional climbing stairs, modern office building, motivational, photorealistic",
    "Resume review scene, professional desk with laptop and documents, clean modern office, realistic lighting",
    "Team meeting in modern conference room, diverse professionals, collaborative atmosphere, photorealistic",
    "Professional woman giving presentation, confident speaker, modern office, business casual attire, realistic",
    "Career coaching session, mentor and mentee, professional office setting, warm lighting, photorealistic",
    "Job search concept, professional using laptop, modern workspace, focused expression, realistic"
]

def initialize_vertex_ai():
    """Initialize Vertex AI"""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

def generate_hr_image(prompt, style="photorealistic"):
    """
    Generate HR-themed image using Vertex AI Imagen
    
    Args:
        prompt: Text prompt for image generation
        style: Image style (photorealistic, illustration, etc.)
        
    Returns:
        PIL Image object
    """
    try:
        print(f"🎨 Generating image: {prompt[:50]}...")
        
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        # Generate image
        response = model.generate_images(
            prompt=f"{prompt}, {style}, high quality, professional, 1080x1080",
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )
        
        # Access images from response
        if response and hasattr(response, 'images') and len(response.images) > 0:
            # Get first image
            generated_image = response.images[0]
            
            # Convert to PIL Image
            from io import BytesIO
            img = Image.open(BytesIO(generated_image._image_bytes))
            print(f"✅ Image generated: {img.size}")
            return img
        
        print("❌ No images in response")
        return None
        
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_text_overlay(image, text, position="bottom", font_size=60, color="#FFFFFF"):
    """
    Add text overlay to image
    
    Args:
        image: PIL Image
        text: Text to overlay
        position: top, center, bottom
        font_size: Font size
        color: Text color
        
    Returns:
        PIL Image with text overlay
    """
    try:
        # Create a copy
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype(FONT_BOLD, font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        max_width = img.width - 100
        lines = textwrap.wrap(text, width=30)
        
        # Calculate text height
        line_height = font_size + 10
        total_height = len(lines) * line_height
        
        # Position
        if position == "top":
            y = 50
        elif position == "center":
            y = (img.height - total_height) // 2
        else:  # bottom
            y = img.height - total_height - 50
        
        # Draw text with outline
        for line in lines:
            # Get text bbox
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            
            # Draw outline (black)
            outline_range = 3
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((x + adj_x, y + adj_y), line, font=font, fill="#000000")
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=color)
            y += line_height
        
        return img
        
    except Exception as e:
        print(f"Text overlay error: {e}")
        return image

def add_logo_overlay(image, logo_path, position="top-right", size=150, opacity=0.9):
    """
    Add logo overlay to image
    
    Args:
        image: PIL Image
        logo_path: Path to logo file
        position: top-left, top-right, bottom-left, bottom-right
        size: Logo width
        opacity: Logo opacity (0-1)
        
    Returns:
        PIL Image with logo
    """
    try:
        if not os.path.exists(logo_path):
            return image
        
        # Load logo
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo
        aspect = logo.height / logo.width
        new_height = int(size * aspect)
        logo = logo.resize((size, new_height), Image.Resampling.LANCZOS)
        
        # Apply opacity
        if opacity < 1.0:
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            logo.putalpha(alpha)
        
        # Position
        margin = 30
        if position == "top-left":
            pos = (margin, margin)
        elif position == "top-right":
            pos = (image.width - size - margin, margin)
        elif position == "bottom-left":
            pos = (margin, image.height - new_height - margin)
        else:  # bottom-right
            pos = (image.width - size - margin, image.height - new_height - margin)
        
        # Paste logo
        img = image.copy().convert("RGBA")
        img.paste(logo, pos, logo)
        
        return img.convert("RGB")
        
    except Exception as e:
        print(f"Logo overlay error: {e}")
        return image

def add_contact_info(image, contact_details, position="bottom"):
    """
    Add contact information overlay
    
    Args:
        image: PIL Image
        contact_details: Dict with contact info
        position: bottom or top
        
    Returns:
        PIL Image with contact info
    """
    try:
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype(FONT_REGULAR, 28)
        except:
            font = ImageFont.load_default()
        
        # Build contact text
        contact_text = []
        if contact_details.get('website'):
            contact_text.append(f"🌐 {contact_details['website']}")
        if contact_details.get('email'):
            contact_text.append(f"📧 {contact_details['email']}")
        if contact_details.get('phone'):
            contact_text.append(f"📱 {contact_details['phone']}")
        
        if not contact_text:
            return image
        
        # Position
        y = img.height - 120 if position == "bottom" else 30
        
        # Draw semi-transparent background
        bg_height = len(contact_text) * 35 + 20
        bg_y = y - 10
        draw.rectangle(
            [(0, bg_y), (img.width, bg_y + bg_height)],
            fill=(0, 0, 0, 180)
        )
        
        # Draw contact info
        for line in contact_text:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            draw.text((x, y), line, font=font, fill="#FFFFFF")
            y += 35
        
        return img
        
    except Exception as e:
        print(f"Contact info error: {e}")
        return image

def generate_branded_image_post(
    topic,
    research_data=None,
    client_details=None,
    add_logo=True,
    add_contact=True
):
    """
    Generate complete branded image post
    
    Args:
        topic: Post topic/title
        research_data: Research insights (optional)
        client_details: Client details dict
        add_logo: Whether to add logo
        add_contact: Whether to add contact info
        
    Returns:
        Path to generated image
    """
    print("="*70)
    print("🎨 BRANDED IMAGE POST GENERATION")
    print("="*70)
    print(f"Topic: {topic}")
    print("="*70)
    print()
    
    # Initialize Vertex AI
    initialize_vertex_ai()
    
    # Select random HR prompt or use research-based prompt
    if research_data and research_data.get('research'):
        # Extract key visual from research
        base_prompt = random.choice(HR_PROMPTS)
    else:
        base_prompt = random.choice(HR_PROMPTS)
    
    # Generate base image
    print("🎨 Step 1: Generating base image...")
    base_image = generate_hr_image(base_prompt)
    
    if not base_image:
        print("❌ Failed to generate base image")
        return None
    
    # Add text overlay
    print("📝 Step 2: Adding text overlay...")
    image_with_text = add_text_overlay(
        base_image,
        topic.upper(),
        position="bottom",
        font_size=70,
        color=BRAND_COLORS["gold"]
    )
    
    # Randomly decide to add logo (70% chance)
    if add_logo and random.random() < 0.7:
        print("🎨 Step 3: Adding logo...")
        logos = [os.path.join(PNG_DIR, f) for f in os.listdir(PNG_DIR) if f.endswith('.png')]
        if logos:
            logo_path = random.choice(logos)
            logo_position = random.choice(["top-left", "top-right", "bottom-left", "bottom-right"])
            image_with_text = add_logo_overlay(
                image_with_text,
                logo_path,
                position=logo_position,
                size=random.randint(120, 180)
            )
    
    # Add contact info if enabled
    if add_contact and client_details and client_details.get('contact_info'):
        print("📞 Step 4: Adding contact info...")
        image_with_text = add_contact_info(
            image_with_text,
            client_details['contact_info'],
            position="bottom"
        )
    
    # Save image
    timestamp = int(time.time())
    filename = f"branded_post_{timestamp}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    image_with_text.save(output_path, quality=95)
    
    print()
    print("="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print(f"📁 File: {output_path}")
    print(f"📋 Filename: {filename}")
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
    
    # Test generation
    # generate_branded_image_post(
    #     topic="Interview Success Tips",
    #     client_details=client_details,
    #     add_logo=True,
    #     add_contact=True
    # )
    
    print("✅ Image post generator module loaded. Ready to use.")
