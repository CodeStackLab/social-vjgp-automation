import os
from google import genai

BASE_DIR = "/root/.gemini/antigravity/scratch/social_automato"
APP_DIR = os.path.join(BASE_DIR, "app")
CREDENTIALS_PATH = os.path.join(APP_DIR, "google_credentials.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_PATH
PROJECT_ID = "julia-ai-automation"
LOCATION = "us-central1"
TARGET_OP = "projects/julia-ai-automation/locations/us-central1/publishers/google/models/veo-3.1-generate-preview/operations/ea83c15f-ea74-4502-8ec4-b1419fdefb93"

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print("Listing operations...")
# Try list
try:
    # Need to verify if list takes arguments or if it's on a different path
    # Usually list(name=parent)
    # parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-generate-preview"
    # Actually operations are usually at location level or global?
    # Let's try client.operations.list()
    # It might return an iterator
    pager = client.operations.list()
    
    found = False
    for op in pager:
        if op.name == TARGET_OP:
            print(f"✅ Found target operation!")
            if op.done:
                print("Operation is done.")
                # Inspect result
                res = op.result
                print(f"Result type: {type(res)}")
                if res and hasattr(res, 'generated_videos'):
                    vid = res.generated_videos[0].video
                    print(f"Video object dirs: {dir(vid)}")
                    if hasattr(vid, 'uri'):
                         print(f"URI: {vid.uri}")
                found = True
                break
    
    if not found:
        print("❌ Target operation not found in list.")

except Exception as e:
    print(f"❌ Error listing: {e}")
