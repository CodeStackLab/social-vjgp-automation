
import os
import video_engine
from dotenv import load_dotenv

# Load env
load_dotenv()

print("Starting generation...")

# Script text for the video
script = "Unlock your potential with VirtualJobGuru. Expert guidance for your HR career."

# Call branded video generation
# We don't pass creds explicitly as it loads from ENV/Default
path, filename = video_engine.create_branded_video(
    script,
    title="Career Success"
)

if path:
    print(f"SUCCESS: {filename}")
else:
    print(f"FAILED: {filename}")
