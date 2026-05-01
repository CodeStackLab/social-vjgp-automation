import sys
import os
from unittest.mock import MagicMock

# Add app to path
sys.path.insert(0, "/root/.gemini/antigravity/scratch/social_automato/app")

import video_engine

# Mock generate_video_asset to return existing file
EXISTING_VIDEO = "/root/.gemini/antigravity/scratch/social_automato/app/generated_media/temp/gen_clip_1770480532786.mp4"

def mock_generate(*args, **kwargs):
    print(f"[MOCK] Returning existing video: {EXISTING_VIDEO}")
    return EXISTING_VIDEO

video_engine.generate_video_asset = mock_generate

# Load Credentials from Settings (mimicking run_veo_gen.py)
try:
    import json
    base_dir = "/root/.gemini/antigravity/scratch/social_automato"
    config_path = os.path.join(base_dir, 'data/app_settings.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            settings = json.load(f)
            creds_json = settings.get('api_config', {}).get('google_cloud_json')
            if creds_json:
                creds_path = "/tmp/gcp_creds_test.json"
                if isinstance(creds_json, str):
                    with open(creds_path, "w") as cf:
                        cf.write(creds_json)
                else:
                    with open(creds_path, "w") as cf:
                        json.dump(creds_json, cf)
                
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                print(f"🔑 Auth: Credentials loaded from app_settings.json")
            else:
                print("⚠️ No Service Account JSON found in settings.")
    else:
        print(f"⚠️ app_settings.json not found at {config_path}")
except Exception as e:
    print(f"Error loading credentials: {e}")

# Run create_branded_video with subtitles
print("🚀 Starting Subtitle Test...")
output_path, filename = video_engine.create_branded_video(
    script_text="Test Script",
    title="Subtitle Test",
    visual_prompt=None,
    subtitles=True,
    target_clips=1
)

if output_path and os.path.exists(output_path):
    print(f"✅ Auto-Subtitle Test Passed!")
    print(f"📁 Output: {output_path}")
else:
    print("❌ Auto-Subtitle Test Failed!")
