"""
High Quality Image Post Generator
Generates "poster style" social media images with minimal branding
"""

import os
import sys
import time
import random
import textwrap
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Add app to path for imports if needed
sys.path.insert(0, '/app')

# Vertex AI imports
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# Configuration
# Manual .env loading
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
env_vars = {}
if os.path.exists(env_path):
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"⚠️ Error loading .env: {e}")

PROJECT_ID = env_vars.get('GCP_PROJECT_ID') or os.environ.get('GOOGLE_CLOUD_PROJECT') or 'julia-ai-automation'
LOCATION = "us-central1"
GEMINI_API_KEY = env_vars.get('GEMINI_API_KEY')

# OUTPUT_DIR = "/app/generated_media/images"
# Use relative path to ensure it works both locally and in container (if mounted correctly)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_media", "images")
# Updated to the correct path found during research
ASSETS_DIR = "/root/.gemini/antigravity/scratch/social_automato/assets"
PNG_DIR = os.path.join(ASSETS_DIR, "Virtual Job Guru/Final Files/Final Files/PNG Files")

# Fonts - adjusted paths based on existing code
FONT_BOLD = "/root/.gemini/antigravity/scratch/social_automato/assets/fonts/Montserrat-Bold.ttf"
FONT_REGULAR = "/root/.gemini/antigravity/scratch/social_automato/assets/fonts/Montserrat-Regular.ttf"

# Brand colors
BRAND_COLORS = {
    "primary_orange": "#FF8D1F",
    "black": "#000000",
    "white": "#FFFFFF",
    "dark_blue": "#0F172A",
    "gold": "#FFD700"
}

# Improved "Poster Style" Prompts
# focusing on high quality, cinematic, editorial looks with copy space
POSTER_PROMPTS = [
    "cinematic shot of a professional workspace, shallow depth of field, editorial photography, magazine quality, 8k, highly detailed, dramatic lighting, negative space for text",
    "minimalist modern office aesthetic, clean lines, soft natural lighting, high end photography, architectural digest style, 8k, copy space on top",
    "close up of hands typing on a laptop, dark moody atmosphere, cyber security concept, matrix style color grading, cinematic, 8k, blurred background for text",
    "futuristic office abstract background, bokeh lights, technology concept, blue and orange color grade, 8k, wallpaper quality, empty space in center",
    "confident business professional silhouette against a city skyline, golden hour, inspiring, success concept, cinematic lighting, 8k, room for text",
    "clean white desk setup, minimal objects, top down view, bright airy, productivity concept, high key photography, 8k, minimalistic background",
    "abstract geometric shapes in brand orange and blue, 3d render, glass morphism, high tech, modern background, 8k, soft focus"
]

def initialize_vertex_ai():
    """Initialize Vertex AI"""
    try:
        # Set project ID explicitly in env for libraries that read it
        os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
        
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Vertex AI: {e}")
        return False

def generate_advice_text_api(topic):
    """
    Generate short advice text using Gemini REST API with key fallback
    """
    print(f"🧠 Generating advice for topic: {topic}")
    
    keys_to_try = []
    if env_vars.get('GEMINI_API_KEY'):
        keys_to_try.append(env_vars.get('GEMINI_API_KEY'))
    if env_vars.get('VERTEX_AI_API_KEY'):
        keys_to_try.append(env_vars.get('VERTEX_AI_API_KEY'))
        
    if not keys_to_try:
        print("⚠️ No API keys found in .env, falling back to topic")
        return topic

    for i, api_key in enumerate(keys_to_try):
        try:
            # Try gemini-1.5-flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            
            prompt_text = f"Write a short, punchy 10-word advice about: {topic}"
            
            data = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            print(f"🔄 Trying Key #{i+1}...")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    advice = result['candidates'][0]['content']['parts'][0]['text']
                    advice = advice.strip().replace('"', '')
                    print(f"💡 Generated Advice: {advice}")
                    return advice
            else:
                print(f"⚠️ API Error (Key #{i+1}): {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Text generation error (Key #{i+1}): {e}")
            
    print("⚠️ All text generation attempts failed. Using topic as fallback.")
    return topic

def generate_high_quality_image(topic, advice_text):
    """
    Generate high quality image using Vertex AI Imagen, or fallback
    """
    print(f"🎨 Generating base image for topic: {topic}")
    
    # Try Vertex AI first
    try:
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        # Construct a rich prompt
        base_prompt = random.choice(POSTER_PROMPTS)
        full_prompt = f"{base_prompt}. Context: {topic}. Text to include: '{advice_text}'. High contrast, copy space for text, sharp focus, professional photography."
        
        print(f"📝 Prompt: {full_prompt}")
        
        response = model.generate_images(
            prompt=full_prompt,
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )
        
        if response and hasattr(response, 'images') and len(response.images) > 0:
            from io import BytesIO
            img = Image.open(BytesIO(response.images[0]._image_bytes))
            print(f"✅ Image generated (Vertex AI): {img.size}")
            return img
            
    except Exception as e:
        print(f"⚠️ Vertex AI Image Gen Failed: {e}")
        print("ℹ️ Check your Google Cloud credentials (gcloud auth application-default login)")
        
    # Fallback to gradient background if Vertex fails
    print("🎨 Generating FALLBACK background...")
    width, height = 1080, 1080
    img = Image.new('RGB', (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    # Create a simple gradient
    for y in range(height):
        r = int(15 + (y / height) * 40)
        g = int(23 + (y / height) * 30)
        b = int(42 + (y / height) * 60)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    return img

def add_poster_text(image, text, position="center", color="#FFFFFF"):
    """
    Add large, bold, poster-style text with shadow/glow
    """
    try:
        img = image.copy()
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Font loading
        font_size = 120 # Starting font size
        try:
            font = ImageFont.truetype(FONT_BOLD, font_size)
        except:
            print("⚠️ Custom font not found, using default")
            font = ImageFont.load_default()
            
        # Text wrapping and sizing
        # We want the text to fill about 85% of the width
        target_width = width * 0.85
        
        # Dynamic font sizing
        lines = []
        while font_size > 40:
            try:
                font = ImageFont.truetype(FONT_BOLD, font_size)
            except:
                pass
                
            # Try wrapping
            avg_char_width = font.getbbox("A")[2] # Approximate
            chars_per_line = int(target_width / avg_char_width)
            lines = textwrap.wrap(text.upper(), width=chars_per_line)
            
            # Check height
            total_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]) * 1.3
            if total_height < height * 0.6: # Don't take up more than 60% height
                break
            font_size -= 5
            
        # Draw text
        line_height = font.getbbox("Tg")[3] - font.getbbox("Tg")[1] + 20
        total_text_height = len(lines) * line_height
        
        # Determine strict Y position based on image analysis could be better, 
        # but for now center-weighted or top/bottom third looks best.
        # Let's try to center it mostly.
        
        y = (height - total_text_height) // 2
            
        # Draw shadow/glow for readability
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw strong drop shadow / outline to ensure readability on ANY background
            outline_color = "#000000"
            steps = 5
            for adj_x in range(-steps, steps+1):
                for adj_y in range(-steps, steps+1):
                    draw.text((x + adj_x, y + adj_y), line, font=font, fill=outline_color)
            
            # Main text
            draw.text((x, y), line, font=font, fill=color)
            
            y += line_height
            
        return img
        
    except Exception as e:
        print(f"❌ Text overlay error: {e}")
        return image

def add_minimal_logo(image):
    """
    Add logo in a corner, clean and simple. 
    Using only logo assets as requested.
    """
    try:
        if not os.path.exists(PNG_DIR):
            print(f"⚠️ Logo directory not found: {PNG_DIR}")
            return image
            
        logos = [f for f in os.listdir(PNG_DIR) if f.endswith('.png')]
        if not logos:
            print("⚠️ No logos found")
            return image
            
        # Prefer specific logo if available, else random
        logo_choice = next((l for l in logos if "white" in l.lower() or "transparent" in l.lower()), random.choice(logos))
        logo_path = os.path.join(PNG_DIR, logo_choice)
        
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo - kept relatively small for "minimal" look
        target_size = 180
        aspect = logo.height / logo.width
        new_height = int(target_size * aspect)
        logo = logo.resize((target_size, new_height), Image.Resampling.LANCZOS)
        
        # Position - Corner (randomly top-left, top-right, bottom-right)
        # Avoid bottom-center as that's often for captions
        padding = 60
        pos_choices = [
            (padding, padding), # Top-Left
            (image.width - target_size - padding, padding), # Top-Right
            (image.width - target_size - padding, image.height - new_height - padding) # Bottom-Right
        ]
        pos = random.choice(pos_choices)
        
        # Paste
        img = image.copy().convert("RGBA")
        img.paste(logo, pos, logo)
        
        return img.convert("RGB")
        
    except Exception as e:
        print(f"❌ Logo overlay error: {e}")
        return image

def generate_poster_post(topic):
    """
    Main function to generate the post
    """
    print("="*60)
    print("🚀 HIGH QUALITY POSTER GENERATOR v3")
    print("="*60)
    
    initialize_vertex_ai()
        
    # 1. Generate Advice Text
    advice_text = generate_advice_text_api(topic)
        
    # 2. Generate Image
    img = generate_high_quality_image(topic, advice_text)
    if not img:
        return None
        
    # 3. Add Text
    img = add_poster_text(img, advice_text, position="center", color="#FFFFFF")
    
    # 4. Add Logo
    img = add_minimal_logo(img)
    
    # 5. Save
    timestamp = int(time.time())
    filename = f"poster_{timestamp}.png"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    output_path = os.path.join(OUTPUT_DIR, filename)
    img.save(output_path, quality=95) # High quality JPG/PNG
    
    # Ensure correct permissions for web serving (644)
    try:
        os.chmod(output_path, 0o644)
    except Exception as e:
        print(f"⚠️ Warning: Could not set permissions: {e}")
    
    print(f"✅ Saved to: {output_path}")
    print(f"🔗 URL: https://vjgu.online/videos/images/{filename}")
    
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="Modern Leadership Principles", help="Topic for the post")
    args = parser.parse_args()
    
    generate_poster_post(args.topic)
