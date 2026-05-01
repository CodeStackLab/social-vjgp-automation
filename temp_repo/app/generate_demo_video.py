import sys
import os
import video_engine
from dotenv import load_dotenv

load_dotenv()

def generate_demo():
    print("Generating 8-second branded demo video...")
    
    # User's specific text
    script_text = "Are you currently looking for a new job and you feel overwhelmed because you just don't know where to start? If that is the case, I have the perfect product for you. My name is Julia and I've been working as a recruiter for the last 20 years. In my one-to-one coaching session, I will guide you step-by-step through the entire process. We will check all your documents and I can guarantee you I will help you in the best way possible. If you're interested, click on the link below."
    
    # Shorten for 8 seconds? 
    # The user provided a LONG text but asked for an 8 second video.
    # 8 seconds is very short for that much text. 
    # I will trim it or just generate the video and let the audio dictate length (Veo usually matches audio).
    # BUT Veo generation is expensive/limited, so for 8 seconds I should prioritize the visual.
    
    # Actually, the user provided a full script with timestamps in the prompt!
    # The prompt JSON shows segments ending at ~30 seconds.
    # But the user request says "please generate 8 second".
    # I will generate an 8-second visual, but the audio might be cut off if I force it on the text.
    # Let's try to generate the video first using the engine defaults (which usually matches audio length).
    # If I force 8 seconds, I should only use the first sentence.
    
    short_script = "Are you looking for a new job and feel overwhelmed? I can help you land your dream role in weeks."
    
    # Visual prompt matching the "Julia" persona
    visual_prompt = "Professional HR recruiter Julia, 40s, warm smile, modern office, speaking directly to camera, cinematic lighting, 4k"
    
    # API credentials
    project_id = os.getenv("VERTEX_PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    
    # Generate
    try:
        # Note: create_branded_video handles text-to-speech, veo generation, and branding overlay
        media_path, filename = video_engine.create_branded_video(
            script_text=short_script, # Use shorter text for 8s constraint
            title="Julia Intro Demo",
            visual_prompt=visual_prompt,
            model_name="veo-3.1-generate-preview", # or 'veo-3.1-generate-preview-pro' if available
            project_id=project_id,
            location=location
        )
        
        print(f"\nSUCCESS! Video generated at:\n{media_path}")
        return media_path
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return None

if __name__ == "__main__":
    generate_demo()
