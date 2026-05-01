import os
import sys
import time

# Mock environment for standalone test
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/.gemini/antigravity/scratch/social_automato/app/vertex-credentials.json"
os.environ["GCP_PROJECT_ID"] = "julia-ai-automation"

sys.path.append("/root/.gemini/antigravity/scratch/social_automato/app")
import video_engine

def test_remix():
    print("Testing Library Asset Remix...")
    
    script = "This is a test script for remixing library assets."
    title = "HR EXPERT INSIGHTS"
    
    # Trigger the remix
    m_path, fname = video_engine.create_library_remix_video(
        script,
        title=title,
        project_id="julia-ai-automation"
    )
    
    if m_path:
        print(f"✅ SUCCESS: {m_path}")
    else:
        print(f"❌ FAILED: {fname}")

if __name__ == "__main__":
    test_remix()
