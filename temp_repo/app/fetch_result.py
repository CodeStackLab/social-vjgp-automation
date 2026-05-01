import os
import sys
from google import genai
from google.genai import types

# Set up credentials
BASE_DIR = "/root/.gemini/antigravity/scratch/social_automato"
APP_DIR = os.path.join(BASE_DIR, "app")
CREDENTIALS_PATH = os.path.join(APP_DIR, "google_credentials.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_PATH

PROJECT_ID = "julia-ai-automation"
LOCATION = "us-central1"
OPERATION_NAME = "projects/julia-ai-automation/locations/us-central1/publishers/google/models/veo-3.1-generate-preview/operations/ea83c15f-ea74-4502-8ec4-b1419fdefb93"

def main():
    print(f"🔧 Using credentials from: {CREDENTIALS_PATH}")
    
    client = genai.Client(
        vertexai=True, 
        project=PROJECT_ID, 
        location=LOCATION
    )
    print(f"🔍 Getting operation: {OPERATION_NAME}")
    # SDK expects an object with .name attribute
    class OpWrapper:
        def __init__(self, name):
            self.name = name
            
    operation = client.operations.get(OpWrapper(OPERATION_NAME))
    
    if not operation.done:
        print("❌ Operation not done yet!")
        return

    print("✅ Operation done.")
    # Access result property (no parentheses based on previous finding)
    result = operation.result
    
    # Inspect result
    print(f"Result type: {type(result)}")
    if hasattr(result, 'generated_videos'):
        print(f"Generated videos count: {len(result.generated_videos)}")
        video_obj = result.generated_videos[0].video
        print(f"Video object type: {type(video_obj)}")
        print(f"Video object dirs: {dir(video_obj)}")
        
        # Try to find data or uri
        video_bytes = None
        if hasattr(video_obj, 'data'):
             print("Found .data attribute")
             video_bytes = video_obj.data
        elif hasattr(video_obj, 'bytes_base64_encoded'):
             print("Found .bytes_base64_encoded attribute")
             import base64
             video_bytes = base64.b64decode(video_obj.bytes_base64_encoded)
        elif hasattr(video_obj, 'uri'):
             print(f"Found .uri attribute: {video_obj.uri}")
             # If it's a URI, we might need to download it (not implemented here yet)
             print("⚠️ Video is at URI, need to download.")
        
        if video_bytes:
            output_path = os.path.join(APP_DIR, "generated_media", "temp_julia_8s_raw.mp4")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            print(f"✅ Video saved to: {output_path}")
        else:
            print("❌ Could not extract video bytes.")
    else:
        print("❌ No generated_videos in result.")
        print(f"Result dirs: {dir(result)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
