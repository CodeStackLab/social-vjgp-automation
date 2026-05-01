import os
import sys
import time
import shutil

# Set paths
PROJ_DIR = "/root/.gemini/antigravity/scratch/social_automato"
sys.path.append(os.path.join(PROJ_DIR, "app"))

import video_engine

def create_interview_tip_post():
    print("🚀 Generating Professional Interview Tip Post...")
    
    # 1. Define Content
    title = "INTERVIEW SUCCESS"
    caption = "The secret to confidence is preparation. Master your story before you walk into the room."
    
    # 2. Generate High-Quality Background
    print("🎨 Generating Background Image (Nano Banana)...")
    bg_prompt = "A professional woman in her 30s confidently shaking hands in a bright, modern corporate office. Authentic smile, blurred office background. Cinematic lighting, photorealistic 8k."
    # Use 'portrait' (4:5) for best cross-platform engagement
    bg_path = video_engine.generate_image_asset(bg_prompt, aspect_ratio="portrait")
    
    if not bg_path:
        print("❌ Background generation failed.")
        return
    
    # 3. Create Branded Image Post (Hero Style)
    print("✍️ Applying Branding and Safe-Zone Text...")
    m_path, fname = video_engine.create_image_post(
        title=title,
        caption=caption,
        bg_path=bg_path,
        style='hero',
        show_branding=True,
        aspect_ratio='portrait'
    )
    
    if m_path:
        print(f"✅ SUCCESS: {m_path}")
        # Copy to artifacts for easy viewing
        artifact_path = "/root/.gemini/antigravity/brain/12a278f7-f91e-4dea-b9e7-4b2e36eb23f3/interview_tip_post.png"
        shutil.copy(m_path, artifact_path)
        print(f"📸 Saved to artifacts: {artifact_path}")
    else:
        print(f"❌ Image Post failed: {fname}")

if __name__ == "__main__":
    create_interview_tip_post()
