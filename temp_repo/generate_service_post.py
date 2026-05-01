import os
import sys
import time

# Set paths
PROJ_DIR = "/root/.gemini/antigravity/scratch/social_automato"
sys.path.append(os.path.join(PROJ_DIR, "app"))

import video_engine

def create_service_post():
    print("🚀 Generating Professional Service Overview Post...")
    
    # 1. Define Content
    title = "CAREER SUCCESS SECRETS"
    services = [
        "• CV & Resume Quick Check",
        "• Interview Preparation Coaching",
        "• Career Coaching Sessions",
        "• Detailed Resume Strategy",
        "• Hiring Insights & Seminars",
        "• Job Search Masterclass"
    ]
    caption = "\n".join(services)
    
    # 2. Generate High-Quality Background
    print("🎨 Generating Background Image...")
    bg_prompt = "A high-end, modern corporate HR office with a clean aesthetic. Large windows with soft natural light. Minimalist desk with a laptop and a small green plant. Professional and calm atmosphere. Photorealistic 8k, bokeh background."
    # Use 'portrait' (4:5) for all platforms
    bg_path = video_engine.generate_image_asset(bg_prompt, aspect_ratio="portrait")
    
    if not bg_path:
        print("❌ Background generation failed.")
        return
    
    # 3. Create Branded Image Post
    print("✍️ Applying Branding and Text...")
    # Using 'list' style for the services with portrait aspect ratio
    m_path, fname = video_engine.create_image_post(
        title=title,
        caption=caption,
        bg_path=bg_path,
        style='list',
        show_branding=True,
        aspect_ratio='portrait'
    )
    
    if m_path:
        print(f"✅ SUCCESS: {m_path}")
        # Copy to artifacts for easy viewing
        artifact_path = "/root/.gemini/antigravity/brain/12a278f7-f91e-4dea-b9e7-4b2e36eb23f3/service_overview_post.png"
        import shutil
        shutil.copy(m_path, artifact_path)
        print(f"📸 Saved to artifacts: {artifact_path}")
    else:
        print(f"❌ Image Post failed: {fname}")

if __name__ == "__main__":
    create_service_post()
