#!/usr/bin/env python3
"""
Simple Veo 3 Fast Test Script
Tests direct video generation from Google Veo 3 Fast model via Vertex AI
No ffmpeg, no branding, no post-processing - just raw Veo 3 output
"""

import os
import time
import requests

# Configuration from environment
VERTEX_PROJECT_ID = "your-project-id"
VERTEX_API_KEY = "YOUR_API_KEY"
VIDEO_MODEL = "veo-3.1-generate-preview"
LOCATION = "us-central1"

def generate_veo3_video(prompt, output_path="test_veo3_video.mp4"):
    """
    Generate video using Veo 3 Fast model via Vertex AI
    
    Args:
        prompt: Text description for video generation
        output_path: Where to save the generated video
    
    Returns:
        tuple: (success: bool, video_path or error_message: str)
    """
    
    print(f"\n{'='*60}")
    print(f"🎬 VEO 3 FAST VIDEO GENERATION TEST")
    print(f"{'='*60}")
    print(f"Model: {VIDEO_MODEL}")
    print(f"Project: {VERTEX_PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")
    
    # Vertex AI endpoint
    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{VERTEX_PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{VIDEO_MODEL}:predict"
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {VERTEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Request payload for Veo 3
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",  # Vertical video for reels/shorts
            "duration": "8s"  # 8 second video
        }
    }
    
    try:
        print("📤 Sending request to Vertex AI...")
        print(f"Endpoint: {endpoint}\n")
        
        # Make the API request
        response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return False, error_msg
        
        result = response.json()
        print(f"✅ Response received successfully\n")
        
        # Extract video data
        if "predictions" in result and len(result["predictions"]) > 0:
            prediction = result["predictions"][0]
            
            # Check for video URL or base64 data
            video_url = None
            video_data = None
            
            if "videoUrl" in prediction:
                video_url = prediction["videoUrl"]
                print(f"🔗 Video URL: {video_url}")
            elif "videoData" in prediction:
                video_data = prediction["videoData"]
                print(f"📦 Video data received (base64 encoded)")
            else:
                error_msg = f"No video data in response: {prediction}"
                print(f"❌ {error_msg}")
                return False, error_msg
            
            # Download or decode video
            print(f"\n💾 Saving video to: {output_path}")
            
            if video_url:
                # Download from URL
                print("⬇️  Downloading video from URL...")
                video_response = requests.get(video_url, timeout=120)
                if video_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    print(f"✅ Video downloaded successfully!")
                else:
                    error_msg = f"Failed to download video: {video_response.status_code}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                    
            elif video_data:
                # Decode base64 data
                import base64
                print("🔓 Decoding base64 video data...")
                video_bytes = base64.b64decode(video_data)
                with open(output_path, 'wb') as f:
                    f.write(video_bytes)
                print(f"✅ Video decoded and saved!")
            
            # Verify file exists and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"\n{'='*60}")
                print(f"✅ SUCCESS!")
                print(f"{'='*60}")
                print(f"📁 File: {output_path}")
                print(f"📊 Size: {file_size / 1024 / 1024:.2f} MB")
                print(f"{'='*60}\n")
                return True, output_path
            else:
                error_msg = "Video file was not created"
                print(f"❌ {error_msg}")
                return False, error_msg
        else:
            error_msg = f"No predictions in response: {result}"
            print(f"❌ {error_msg}")
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out (>5 minutes)"
        print(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg


if __name__ == "__main__":
    # Test prompt
    test_prompt = "A professional office environment with modern furniture, natural lighting streaming through large windows, and a person working confidently at a desk. Cinematic, high quality, vertical 9:16 format."
    
    # Output directory
    output_dir = "/root/.gemini/antigravity/scratch/social_automato/test_videos"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"veo3_test_{int(time.time())}.mp4")
    
    # Generate video
    success, result = generate_veo3_video(test_prompt, output_file)
    
    if success:
        print(f"\n🎉 Video generation successful!")
        print(f"📹 Video saved at: {result}")
        print(f"\nYou can view it at: file://{result}")
    else:
        print(f"\n💥 Video generation failed!")
        print(f"Error: {result}")
