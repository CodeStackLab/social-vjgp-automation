#!/usr/bin/env python3
"""
Script to generate 8s Branded HR Video using standard Veo Audio (User Request)
"""

import sys
import os
import json

# Ensure app directory is in path
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

import video_engine
import research_engine
from google.cloud import aiplatform

# User Specific Prompt
USER_PROMPT = """Create an 8-second professional HR explainer video.
Scene: Corporate office background.
Narration: Calm professional female voice explains 'Employee engagement improves productivity'.
Audio: Soft corporate background music.
Style: Clean, realistic, corporate cinematic."""

def run():
    print("=" * 60)
    print("🎬 GENERATING 8S BRANDED VIDEO (VEO MODEL)")
    print("=" * 60)
    print(f"📌 Prompt: {USER_PROMPT}")

    # Load Credentials from Settings
    try:
        with open('/app/data/app_settings.json', 'r') as f:
            settings = json.load(f)
            # api_key = settings.get('api_config', {}).get('vertex_api_key') # Disable API Key
            project_id = settings.get('api_config', {}).get('vertex_project_id')
            
            # Setup Service Account Credentials for Vertex AI
            creds_json = settings.get('api_config', {}).get('google_cloud_json')
            if creds_json:
                creds_path = "/tmp/gcp_creds.json"
                if isinstance(creds_json, str):
                    with open(creds_path, "w") as cf:
                        cf.write(creds_json)
                else:
                    with open(creds_path, "w") as cf:
                        json.dump(creds_json, cf)
                
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                print(f"🔑 Auth: Using Service Account (Vertex AI) Project: {project_id}")
            else:
                print("⚠️ No Service Account JSON found. Auth might fail.")

    except Exception as e:
        print(f"Error loading settings: {e}")
        return

    # Generate Video
    # passing target_clips=1 to force 8s duration
    video_path, filename = video_engine.create_branded_video(
        script_text="Employee engagement improves productivity", # Fallback script text implies this context
        title="HR Insights",
        visual_prompt=USER_PROMPT,
        model_name="veo-3.1-generate-preview",
        api_key=None, # Force Vertex AI
        project_id=project_id,
        target_clips=1,  # FORCE 8s
        skip_branding=True # NO BRANDING
    )

    if video_path and os.path.exists(video_path):
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS! Video Generated")
        print(f"📁 Path: {video_path}")
        print(f"🌐 URL: https://vjgu.online/videos/videos/{filename}")
        print("=" * 60)
    else:
        print("\n❌ FAILED: Video generation failed")

if __name__ == "__main__":
    run()
