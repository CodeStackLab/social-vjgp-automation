import os
import time
from google import genai
from google.genai import types

def test_nano_banana_content():
    project_id = "julia-ai-automation"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/.gemini/antigravity/scratch/social_automato/app/vertex-credentials.json"
    client = genai.Client(vertexai=True, project=project_id, location="us-central1")
    
    prompt = "Generate a high-quality professional image of an HR expert in a modern office."
    
    print("Generating Content with Nano Banana (Gemini 2.5 Flash Image)...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt
        )
        
        print(f"Response Parts: {len(response.candidates[0].content.parts)}")
        for i, part in enumerate(response.candidates[0].content.parts):
            if part.inline_data:
                mime = part.inline_data.mime_type
                print(f"Part {i}: Image found! Mime: {mime}")
                output_path = f"/root/.gemini/antigravity/scratch/social_automato/generated_media/temp/nano_content_{int(time.time())}.png"
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✅ Saved to: {output_path}")
            else:
                print(f"Part {i}: Text - {part.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_nano_banana_content()
