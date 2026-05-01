
import os
import video_engine
from dotenv import load_dotenv

# Load env
load_dotenv()

print("Starting Image Generation Test...")

try:
    path = video_engine.generate_image_asset("A professional HR office workspace, modern, cinematic lighting")
    if path:
        print(f"SUCCESS: Image generated at {path}")
    else:
        print("FAILED: Image generation returned None")
except Exception as e:
    print(f"ERROR: {e}")
