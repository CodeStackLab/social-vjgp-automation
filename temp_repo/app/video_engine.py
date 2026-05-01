import os
import requests
import random
import time
import textwrap
import json
import base64
import asyncio
import numpy as np  # For image array conversion
from moviepy.editor import *
import moviepy.video.fx.all as vfx
import os
import edge_tts

# Set Google Cloud Credentials if available
cred_path = "/root/.gemini/antigravity/scratch/social_automato/app/vertex-credentials.json"
if os.path.exists(cred_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    print(f"DEBUG: Set GOOGLE_APPLICATION_CREDENTIALS to {cred_path}", flush=True)

from platform_optimizer import PLATFORM_SPECS
# Disabled Vertex AI for Free Engine Setup
genai = None
types = None
ImageGenerationModel = None

from asset_manager import get_flat_assets

try:
    from google.cloud import speech
except ImportError:
    speech = None
    print("WARNING: google-cloud-speech not found. Subtitles will be disabled.")

# Fix for MoviePy/Pillow incompatibility
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def add_text_pil(img, text, position, font_path, font_size, color, max_width=None, align='center', bg_color=None):
    """Draws text on a PIL image with high quality."""
    draw = PIL.ImageDraw.Draw(img)
    try:
        font = PIL.ImageFont.truetype(font_path, font_size)
    except:
        font = PIL.ImageFont.load_default()
        
    # Wrap text
    if max_width:
        avg_char_width = font.getlength("x")
        max_chars = int(max_width / avg_char_width)
        lines = textwrap.wrap(text, width=max_chars)
    else:
        lines = [text]
        
    # Calculate text size
    line_height = font.getbbox("hg")[3] + 10 # approximate height
    text_height = line_height * len(lines)
    max_line_width = max([font.getlength(line) for line in lines])
    
    # Determine position
    # position can be ('center', y), 'center', 'bottom', or (x, y)
    img_w, img_h = img.size
    
    x, y = 0, 0
    
    if position == 'center':
        x = (img_w - max_line_width) / 2
        y = (img_h - text_height) / 2
    elif position == 'bottom':
        x = (img_w - max_line_width) / 2
        y = img_h - text_height - 50
    elif isinstance(position, tuple):
        pos_x, pos_y = position
        if pos_x == 'center':
             x = (img_w - max_line_width) / 2
        else:
             x = pos_x
             
        if pos_y == 'center':
             y = (img_h - text_height) / 2
        else:
             y = pos_y
             
    # Draw Background if needed
    if bg_color:
        padding = 20
        bg_x1 = x - padding
        bg_y1 = y - padding
        bg_x2 = x + max_line_width + padding
        bg_y2 = y + text_height + padding
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color)

    # Draw Text
    current_y = y
    for line in lines:
        line_w = font.getlength(line)
        if align == 'center':
            line_x = x + (max_line_width - line_w) / 2
        else: # left/west
            line_x = x
        
        # Shadow/Outline for better visibility
        shadow_color = (0,0,0)
        draw.text((line_x+2, current_y+2), line, font=font, fill=shadow_color)
        draw.text((line_x, current_y), line, font=font, fill=color)
        current_y += line_height
        
    return img, current_y

# Configuration
# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = "/tmp" # Use tmp to avoid IM permission issues
# Determine correct output directory (handles host vs docker paths)
if os.path.basename(BASE_DIR) == "app":
    # If in app/, check if generated_media is alongside it (host) or if we should stay in /app (docker)
    parent_media = os.path.join(os.path.dirname(BASE_DIR), "generated_media")
    if os.path.exists(parent_media):
        OUTPUT_DIR = parent_media
    else:
        OUTPUT_DIR = os.path.join(BASE_DIR, "generated_media")
else:
    OUTPUT_DIR = os.path.join(BASE_DIR, "generated_media")
LOCATION = "us-central1"

# Brand Assets
PRIMARY_ORANGE = "#FF8D1F"
PRIMARY_ORANGE_RGB = (255, 141, 31)
BLACK = "#000000"
BLACK_RGB = (0, 0, 0)
WHITE = "#FFFFFF"
WHITE_RGB = (255, 255, 255)
LIGHT_GRAY = (244, 244, 244)

FONT_BOLD = "Montserrat-Bold"
FONT_LIGHT = "Montserrat-Light"

# Default Logo
LOGO_ICON = os.path.join(ASSETS_DIR, "logo.png")

# Check for ImageMagick
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

DIRS = {
    "video": os.path.join(OUTPUT_DIR, "videos"),
    "image": os.path.join(OUTPUT_DIR, "temp/images"),
    "temp": os.path.join(OUTPUT_DIR, "temp"),
    "permanent": os.path.join(OUTPUT_DIR, "permanent")
}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)


# Progress Tracking
PROGRESS_FILE = "/app/data/gen_progress.json"

def set_progress(percent, message, is_generating=True):
    try:
        data = {
            "generating": is_generating,
            "percent": percent,
            "message": message,
            "timestamp": time.time()
        }
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def cleanup_old_files():
    now = time.time()
    cutoff = now - (24 * 3600)
    # Only cleanup temp directories, DO NOT touch permanent
    target_dirs = [DIRS["video"], DIRS["image"], DIRS["temp"]]
    for directory in target_dirs:
        if not os.path.exists(directory): continue
        for f in os.listdir(directory):
            f_path = os.path.join(directory, f)
            if os.path.isfile(f_path) and os.path.getmtime(f_path) < cutoff:
                try:
                    os.remove(f_path)
                except: pass



def generate_image_asset(prompt, aspect_ratio="9:16"):
    """Fetches a free stock image from Pixabay (Fallback to Pollinations)."""
    try:
        cleanup_old_files()
        from pixabay_engine import fetch_pixabay_images, download_image
        
        # Clean prompt for better Pixabay search
        search_query = prompt.replace("cinematic", "").replace("8k", "").replace("high quality", "").strip()
        print(f"Searching Pixabay for: {search_query}...", flush=True)
        
        urls = fetch_pixabay_images(search_query, count=1, orientation="vertical" if aspect_ratio=="9:16" else "horizontal")
        if urls:
            img_path = os.path.join(DIRS["temp"], f"pix_{int(time.time()*1000)}.jpg")
            if download_image(urls[0], img_path):
                return img_path
        
        # Fallback to Pollinations AI (Free)
        print("Fallback to Pollinations AI...", flush=True)
        encoded_prompt = requests.utils.quote(prompt)
        p_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
        img_path = os.path.join(DIRS["temp"], f"poll_{int(time.time()*1000)}.jpg")
        r = requests.get(p_url)
        if r.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(r.content)
            return img_path
            
        return None
    except Exception as e:
        print(f"Image Fetch Error: {e}")
        return None

def generate_video_asset(prompt, project_id=None, model_name="veo-3.1-fast-generate-001", api_key=None):
    """Generates a high-quality video clip using Vertex AI Veo."""
    try:
        cleanup_old_files()
        
        if not project_id:
            print("Video Generation Error: No Project ID provided!", flush=True)
            return None
        
        # Use service account credentials
        from google.oauth2 import service_account
        import google.auth.transport.requests
        import requests
        
        # Load service account credentials
        credentials_path = os.path.join(os.path.dirname(__file__), 'vertex-credentials.json')
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Get access token
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        
        print(f"Generating CLIP via {model_name} (Project: {project_id})... Prompt: {prompt}", flush=True)
        
        # Prepare API request
        location = "us-central1"
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "aspectRatio": "9:16",
                "durationSeconds": 8,
                "sampleCount": 1
            }
        }
        
        # Use a session with retries for better stability
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        
        # Make the request
        print(f"Sending generation request to {model_name}...", flush=True)
        response = session.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        operation_data = response.json()
        
        operation_name = operation_data.get("name")
        print(f"Operation created: {operation_name}", flush=True)
        
        # Poll for completion using fetchPredictOperation endpoint
        fetch_operation_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:fetchPredictOperation"
        
        max_wait = 600  # 10 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            fetch_payload = {"operationName": operation_name}
            op_response = session.post(fetch_operation_url, headers=headers, json=fetch_payload, timeout=30)
            op_response.raise_for_status()
            op_data = op_response.json()
            
            if op_data.get("done"):
                print("Video generation complete!", flush=True)
                
                # Extract video from response
                # Response structure: {"response": {"videos": [{"gcsUri": "...", "mimeType": "..."}]}}
                if "response" in op_data:
                    response_data = op_data["response"]
                    
                    # Check for videos array
                    if "videos" in response_data and len(response_data["videos"]) > 0:
                        video_info = response_data["videos"][0]
                        
                        # Check for base64 encoded video (most common)
                        video_b64 = video_info.get("bytesBase64Encoded")
                        if video_b64:
                            print("Decoding base64 video data...", flush=True)
                            video_bytes = base64.b64decode(video_b64)
                            video_filename = f"gen_clip_{int(time.time()*1000)}.mp4"
                            video_path = os.path.join(DIRS["temp"], video_filename)
                            
                            with open(video_path, "wb") as f:
                                f.write(video_bytes)
                            
                            print(f"Clip saved: {video_path}", flush=True)
                            return video_path
                        
                        # Fallback: Check for GCS URI
                        gcs_uri = video_info.get("gcsUri")
                        if gcs_uri:
                            print(f"Video available at GCS: {gcs_uri}", flush=True)
                            
                            # Download from GCS using authenticated request
                            # Convert gs:// to https://storage.googleapis.com/
                            if gcs_uri.startswith("gs://"):
                                bucket_path = gcs_uri.replace("gs://", "")
                                download_url = f"https://storage.googleapis.com/{bucket_path}"
                                
                                print(f"Downloading video from: {download_url}", flush=True)
                                video_response = requests.get(download_url, headers=headers)
                                video_response.raise_for_status()
                                
                                video_filename = f"gen_clip_{int(time.time()*1000)}.mp4"
                                video_path = os.path.join(DIRS["temp"], video_filename)
                                
                                with open(video_path, "wb") as f:
                                    f.write(video_response.content)
                                
                                print(f"Clip saved: {video_path}", flush=True)
                                return video_path
                    
                    # Fallback: Check for predictions array (base64 format - older API)
                    elif "predictions" in response_data and len(response_data["predictions"]) > 0:
                        predictions = response_data["predictions"]
                        video_b64 = predictions[0].get("bytesBase64Encoded")
                        if video_b64:
                            video_bytes = base64.b64decode(video_b64)
                            video_filename = f"gen_clip_{int(time.time()*1000)}.mp4"
                            video_path = os.path.join(DIRS["temp"], video_filename)
                            
                            with open(video_path, "wb") as f:
                                f.write(video_bytes)
                            
                            print(f"Clip saved: {video_path}", flush=True)
                            return video_path
                
                # Debug: print response structure
                print(f"Response structure: {json.dumps(op_data, indent=2)[:500]}...", flush=True)
                print("No video data in response", flush=True)
                break
            
            print("Video generation in progress...", flush=True)
            time.sleep(10)  # Poll every 10 seconds
        
        print("Video generation timed out", flush=True)
            
    except Exception as e:
        print(f"Video Generation Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    return None

def extend_video_asset(prompt, video_path, project_id=None, model_name="veo-3.1-generate-preview", api_key=None):
    """Extends a video clip using Vertex AI Veo 3.1 Extension."""
    try:
        cleanup_old_files()
        
        if not project_id:
            print("Video Extension Error: No Project ID!", flush=True)
            return None
        
        # Load service account credentials
        from google.oauth2 import service_account
        import google.auth.transport.requests
        import requests
        import base64
        
        credentials_path = os.path.join(os.path.dirname(__file__), 'vertex-credentials.json')
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        
        # Read video and encode to base64
        with open(video_path, "rb") as video_file:
            video_b64 = base64.b64encode(video_file.read()).decode('utf-8')
            
        print(f"Extending video with prompt: {prompt}", flush=True)
        
        location = "us-central1"
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Parameters for extension
        duration = 7 # Documentation says extension is 7s
        bucket_name = "vjgu-video-generation"
        storage_uri = f"gs://{bucket_name}/video-extension-{int(time.time()*1000)}.mp4"
        
        payload = {
            "instances": [{
                "prompt": prompt,
                "video": {
                    "bytesBase64Encoded": video_b64,
                    "mimeType": "video/mp4"
                }
            }],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "9:16",
                "storageUri": storage_uri 
            }
        }
        
        # Add duration if it's not the default or if model supports it
        if "fast" not in model_name:
            payload["parameters"]["durationSeconds"] = duration

        # Manual retry loop for robust SSL handling
        import requests.exceptions
        
        max_retries = 5
        base_delay = 2
        
        response = None
        for attempt in range(max_retries):
            try:
                print(f"Sending extension request to {model_name} (Attempt {attempt+1}/{max_retries})...", flush=True)
                # Create a fresh session for each attempt to avoid stale connection state
                with requests.Session() as session:
                    response = session.post(url, headers=headers, json=payload, timeout=90)
                    
                if response.status_code == 200:
                    break
                elif response.status_code in [500, 502, 503, 504]:
                    print(f"Server Error {response.status_code}, retrying...", flush=True)
                else:
                    # Client error or other non-retriable status
                    print(f"Extension API Error: {response.status_code} - {response.text}", flush=True)
                    response.raise_for_status()
                    break
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"Connection/SSL Error on attempt {attempt+1}: {e}", flush=True)
                if attempt == max_retries - 1:
                    print("All Python retries failed. Proceeding to fallback...", flush=True)
                    response = None # Ensure logic proceeds to fallback
                    break
            
            # Wait before retry with exponential backoff
            sleep_time = base_delay * (2 ** attempt)
            print(f"Waiting {sleep_time}s before next retry...", flush=True)
            time.sleep(sleep_time)
            
        if not response:
            print("Python requests failed. Attempting CURL fallback...", flush=True)
            import subprocess
            import tempfile
            
            # Write payload to temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                json.dump(payload, f)
                payload_path = f.name
            
            try:
                cmd = [
                    "curl", "-X", "POST",
                    url,
                    "-H", f"Authorization: Bearer {access_token}",
                    "-H", "Content-Type: application/json",
                    "-d", f"@{payload_path}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    try:
                        resp_json = json.loads(result.stdout)
                        if "error" in resp_json:
                             print(f"CURL API Error: {resp_json['error']}", flush=True)
                             return None
                        
                        # Mock a response object for consistency
                        class MockResponse:
                            def __init__(self, json_data):
                                self.json_data = json_data
                                self.status_code = 200
                            def json(self):
                                return self.json_data
                        
                        response = MockResponse(resp_json)
                        print("CURL request successful.", flush=True)
                        
                    except json.JSONDecodeError:
                        print(f"CURL Invalid JSON: {result.stdout}", flush=True)
                        return None
                else:
                    print(f"CURL Failed: {result.stderr}", flush=True)
                    return None
            finally:
                if os.path.exists(payload_path):
                    os.remove(payload_path)
            
        if not response:
             raise Exception("All extension attempts failed (Python + CURL)")
            
        operation_name = response.json().get("name")
        print(f"Extension Operation created: {operation_name}", flush=True)
        
        # Polling logic
        fetch_operation_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:fetchPredictOperation"
        
        max_wait = 600 
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            fetch_payload = {"operationName": operation_name}
            op_response = session.post(fetch_operation_url, headers=headers, json=fetch_payload, timeout=30)
            if op_response.status_code != 200:
                print(f"Poll Error: {op_response.status_code} - {op_response.text}", flush=True)
                op_response.raise_for_status()
                
            op_data = op_response.json()
            
            if op_data.get("done"):
                error_data = op_data.get("error")
                if error_data:
                    print(f"Extension Operation Error: {error_data}", flush=True)
                    return None

                response_data = op_data.get("response", {})
                
                # If we used storageUri, we may need to get the actual path from response
                actual_gcs_uri = storage_uri
                if "videos" in response_data and len(response_data["videos"]) > 0:
                    actual_gcs_uri = response_data["videos"][0].get("gcsUri", storage_uri)
                elif "predictions" in response_data and len(response_data["predictions"]) > 0:
                    actual_gcs_uri = response_data["predictions"][0].get("gcsUri", storage_uri)

                print(f"Extension completed. Downloading from {actual_gcs_uri}...", flush=True)
                try:
                    from google.cloud import storage
                    storage_client = storage.Client(project=project_id, credentials=credentials)
                    
                    # Parse actual URI
                    if actual_gcs_uri.startswith("gs://"):
                        parts = actual_gcs_uri.replace("gs://", "").split("/", 1)
                        res_bucket_name = parts[0]
                        blob_path = parts[1]
                    else:
                        res_bucket_name = bucket_name
                        blob_path = actual_gcs_uri
                        
                    bucket = storage_client.bucket(res_bucket_name)
                    blob = bucket.blob(blob_path)
                    
                    video_filename = f"gen_ext_{int(time.time()*1000)}.mp4"
                    out_path = os.path.join(DIRS["temp"], video_filename)
                    
                    blob.download_to_filename(out_path)
                    print(f"Downloaded extension to: {out_path}", flush=True)
                    return out_path
                except Exception as e:
                    print(f"GCS Download Error: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    
                    # Try CURL fallback for GCS
                    print("Attempting CURL GCS Download...", flush=True)
                    import urllib.parse
                    encoded_blob_path = urllib.parse.quote(blob_path, safe='')
                    
                    # Construct API URL
                    download_url = f"https://storage.googleapis.com/storage/v1/b/{res_bucket_name}/o/{encoded_blob_path}?alt=media"
                    
                    video_filename = f"gen_ext_curl_{int(time.time()*1000)}.mp4"
                    out_path = os.path.join(DIRS["temp"], video_filename)
                    
                    cmd = [
                        "curl", "-X", "GET",
                        download_url,
                        "-H", f"Authorization: Bearer {access_token}",
                        "-o", out_path
                    ]
                    
                    import subprocess
                    result = subprocess.run(cmd, capture_output=True)
                    if result.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                         print(f"Downloaded extension via CURL to: {out_path}", flush=True)
                         return out_path
                    else:
                         print(f"CURL Download Failed. Return Code: {result.returncode}", flush=True)
                         print(f"Stderr: {result.stderr}", flush=True)
                         if os.path.exists(out_path):
                             with open(out_path, 'r', errors='ignore') as f:
                                 print(f"File Content (first 500 chars): {f.read(500)}", flush=True)
                    
                    # Fallback to checking response body if download fails
                    video_info = None
                    if "videos" in response_data and len(response_data["videos"]) > 0:
                        video_info = response_data["videos"][0]
                    elif "predictions" in response_data and len(response_data["predictions"]) > 0:
                        video_info = response_data["predictions"][0]
                        
                    if video_info:
                        video_b64_res = video_info.get("bytesBase64Encoded")
                        if video_b64_res:
                            video_bytes = base64.b64decode(video_b64_res)
                            video_filename = f"gen_ext_{int(time.time()*1000)}.mp4"
                            out_path = os.path.join(DIRS["temp"], video_filename)
                            with open(out_path, "wb") as f:
                                f.write(video_bytes)
                            return out_path
                
                print(f"Extension Done but no video data. Data: {json.dumps(op_data)[:500]}", flush=True)
                break
            
            print("Extension in progress...", flush=True)
            time.sleep(15)
            
    except Exception as e:
        print(f"Extension Error: {e}", flush=True)
    return None

def mix_audio_ffmpeg(clip_path, background_path, output_path, bg_volume=0.3):
    """Mixes main audio with background asset using FFmpeg for high performance."""
    try:
        # Use FFmpeg filter_complex to mix audios
        # [0:a] is main, [1:a] is background
        cmd = [
            'ffmpeg', '-y',
            '-i', clip_path,
            '-i', background_path,
            '-filter_complex', f'[1:a]volume={bg_volume}[bg];[0:a][bg]amix=inputs=2:duration=first[a]',
            '-map', '0:v',
            '-map', '[a]',
            '-c:v', 'copy', # Copy video stream, only re-encode audio
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"FFmpeg Mix Error: {e}")
        return False

def generate_audio_speech(text):
    """Generates speech using Google Cloud TTS with SSML for slower pacing."""
    try:
        print("Using Official Client for TTS...", flush=True)
        # The client will automatically use GOOGLE_APPLICATION_CREDENTIALS set at module level
        client = texttospeech.TextToSpeechClient()
        
        # Add breaks for slower pacing using SSML
        sentences = text.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
        ssml_text = "<speak>"
        for s in sentences:
            if s.strip():
                ssml_text += f"{s.strip()} <break time='600ms'/> "
        ssml_text += "</speak>"

        input_text = texttospeech.SynthesisInput(ssml=ssml_text)
        
        is_hindi = any('\u0900' <= c <= '\u097F' for c in text)
        gender_type = random.choice([texttospeech.SsmlVoiceGender.FEMALE, texttospeech.SsmlVoiceGender.MALE])
        gender_str = "female" if gender_type == texttospeech.SsmlVoiceGender.FEMALE else "male"
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="hi-IN" if is_hindi else "en-US",
            ssml_gender=gender_type
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.85 
        )
        
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        
        audio_path = os.path.join(DIRS["temp"], f"audio_{int(time.time()*1000)}.mp3")
        with open(audio_path, "wb") as out:
            out.write(response.audio_content)
        return audio_path, gender_str

    except Exception as e:
        print(f"Official TTS Error: {e}. Falling back to REST...", flush=True)
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            url = "https://texttospeech.googleapis.com/v1/text:synthesize"
            auth_url = f"{url}?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": "hi-IN" if any('\u0900' <= c <= '\u097F' for c in text) else "en-US",
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {"audioEncoding": "MP3"}
            }
            resp = requests.post(auth_url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            audio_content = base64.b64decode(resp.json()["audioContent"])
            
            audio_path = os.path.join(DIRS["temp"], f"audio_{int(time.time()*1000)}.mp3")
            with open(audio_path, "wb") as out:
                out.write(audio_content)
            return audio_path, "female"
        except Exception as e2:
            print(f"TTS Fallback Error: {e2}")
            return None, "female"

def get_random_brand_logo():
    """Selects a random logo from the brand assets directory."""
    logos = []
    png_dir = os.path.join(ASSETS_DIR, "logo")
    if os.path.exists(png_dir):
        for f in os.listdir(png_dir):
            if f.lower().endswith('.png'):
                logos.append(os.path.join(png_dir, f))
    return random.choice(logos) if logos else LOGO_ICON

def transcribe_audio_file(audio_path):
    """Transcribes audio using Google Cloud Speech-to-Text."""
    if not speech:
        print("Speech module not available.")
        return []
    
    try:
        client = speech.SpeechClient()
        
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        
        # Detect encoding from extension
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        sample_rate = 16000
        
        if audio_path.lower().endswith('.mp3'):
            encoding = speech.RecognitionConfig.AudioEncoding.MP3
            sample_rate = 24000 # Standard for Google TTS
            
        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=sample_rate,
            language_code="en-US",
            enable_word_time_offsets=True,
            model="video"
        )

        response = client.recognize(config=config, audio=audio)
        
        transcript_data = []
        for result in response.results:
            alternative = result.alternatives[0]
            for word_info in alternative.words:
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                transcript_data.append({
                    "word": word_info.word,
                    "start": start_time,
                    "end": end_time
                })
        return transcript_data
    except Exception as e:
        print(f"Transcription Error: {e}")
        return []

def generate_subtitle_clips(transcript_data, videosize):
    """Generates MoviePy TextClips from transcription data."""
    if not transcript_data:
        return []
    
    w, h = videosize
    clips = []
    
    # Group words into chunks of ~3-4 words for readability
    chunk_size = 4
    for i in range(0, len(transcript_data), chunk_size):
        chunk = transcript_data[i:i+chunk_size]
        text = " ".join([w['word'] for w in chunk])
        start = chunk[0]['start']
        end = chunk[-1]['end']
        duration = end - start
        if duration < 0.5: duration = 0.5 # Min duration

        # Create Styling: White text on Black background
        txt = (TextClip(text.upper(), fontsize=50, font='Montserrat-Bold', 
                       color='white', bg_color='black', method='caption',
                       size=(w*0.8, None), align='center')
               .set_position(('center', 'center'))
               .set_start(start)
               .set_duration(duration))
        clips.append(txt)
        
    return clips

def create_branded_video(script_text, title="Success Tip", visual_prompt=None, model_name="veo-3.1-generate-preview", api_key=None, project_id=None, **kwargs):
    """
    Creates a premium 20-30s branded video for VirtualJobGuru.
    Features random HR/Training scenes.
    Removes manual TTS as per request (relies on Veo generated audio or silent).
    """
    try:
        w, h = 1080, 1920

        # 1. Determine Duration
        # User Request: Video 30s + Branding (Intro + Outro = 6s max)
        # Main Body: 24-30s
        # Intro: 1.5s
        # Outro: 3s
        # Total: ~30-35s
        # Veo 3.1 generates 8s clips
        
        clip_duration = 8 
        
        if kwargs.get('target_clips'):
            num_clips = kwargs.get('target_clips')
            total_duration = num_clips * clip_duration
        else:
            total_duration = random.randint(24, 32)
            num_clips = int(total_duration / clip_duration)
            if total_duration % clip_duration != 0:
                num_clips += 1

        
        # 2. Generate Random Prompts (Includes "People Trending Interviews" & Guide Training)
        hr_prompts = [
            "A charismatic HR trainer giving a speech to a corporate audience, holding a microphone, professional office, 4k",
            "A viral interview clip style, two people sitting with microphones, podcast setup, discussing career growth, high quality",
            "A corporate mentor standing by a digital screen explaining a diagram, speaking passionately",
            "An HR professional speaking directly to camera, friendly, approachable, explaining a concept",
            "A dynamic group discussion in a modern glass meeting room, candidates debating",
            "A hiring manager reviewing a resume and nodding approval, cinematic lighting",
            "A career coach holding a tablet and giving advice, realistic office ambient, speaking"
        ]
        
        if visual_prompt:
            selected_prompts = [visual_prompt] * num_clips
        else:
            selected_prompts = random.sample(hr_prompts, min(num_clips, len(hr_prompts)))
            # Fill rest if needed
            while len(selected_prompts) < num_clips:
                selected_prompts.append(random.choice(hr_prompts))
            
        p_id = os.getenv("GCP_PROJECT_ID")
        clip_paths = []

        set_progress(5, f"Initializing generation for {num_clips} clips...", is_generating=True)
        
        # PARALLEL GENERATION OPTIMIZATION
        # Generating sequentially takes ~1.5 mins per clip (total 10+ mins).
        # Parallel generation takes ~2-3 mins total (bounded by slowest clip).
        
        import concurrent.futures
        
        def generate_single_clip_wrapper(index, prompt, pid, model, key):
            print(f"Starting Clip {index+1}...", flush=True)
            # Veo specific keywords
            full_prompt = f"{prompt}, high depth cinematography, vertical video, high quality audio, crisp sound, ambient noise"
            path = generate_video_asset(full_prompt, project_id=pid, model_name=model, api_key=key)
            return (index, path)

        clip_paths = [None] * num_clips
        completed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_clips) as executor:
            future_to_index = {
                executor.submit(generate_single_clip_wrapper, i, p, project_id or p_id, model_name, api_key): i 
                for i, p in enumerate(selected_prompts)
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                res_index, res_path = future.result()
                completed_count += 1
                clip_paths[res_index] = res_path
                
                # Update progress based on completion count
                percent = 10 + int((completed_count / num_clips) * 70)
                set_progress(percent, f"Generated clip {completed_count} of {num_clips} (Parallel Mode)...")
                print(f"Clip {completed_count}/{num_clips} Completed.", flush=True)

        # Filter out failed paths (None)
        clip_paths = [p for p in clip_paths if p is not None]
        
        if kwargs.get('skip_branding') and clip_paths:
             print("Skipping branding as per request. Returning raw clip.")
             return clip_paths[0], os.path.basename(clip_paths[0])

        # --- USER ASSET MIXING LOGIC ---
        user_clips_paths = []
        try:
            all_assets = get_flat_assets()
            video_assets = [a for a in all_assets if a.get('category') == 'videos']
            
            # Filter valid paths (check if file exists)
            # Paths in asset manager are relative like "permanent/videos/..." or "assets/..."
            # We need absolute paths.
            valid_user_videos = []
            for va in video_assets:
                # Construct absolute path
                if va['path'].startswith('assets/'):
                    abs_path = os.path.join(BASE_DIR, va['path'])
                elif va['path'].startswith('permanent/'):
                     abs_path = os.path.join(OUTPUT_DIR, va['path'])
                else:
                    # Fallback check
                     abs_path = os.path.join(OUTPUT_DIR, va['path'])
                
                if os.path.exists(abs_path):
                    valid_user_videos.append(abs_path)
            
            if valid_user_videos:
                # Strategy: Mix 50/50 or at least 1-2 user clips
                # We have 'clip_paths' (AI clips). 
                # Let's say we want to inject user clips between them or replace some.
                # User request: "include in between ai genated video ... video clip hai vo saath me paly ho between"
                
                # Let's limit to 1-2 user clips to avoid taking over too much
                num_user_clips = min(len(valid_user_videos), random.randint(1, 2))
                user_clips_paths = random.sample(valid_user_videos, num_user_clips)
                print(f"mixing {len(user_clips_paths)} user videos into generation.")
                
        except Exception as e:
            print(f"Error fetching user assets: {e}")

        # Interleave AI clips and User clips
        # AI, User, AI, User, AI...
        final_sequence_paths = []
        ai_idx = 0
        user_idx = 0
        
        # We want to start with AI usually to set the scene, unless we have no AI clips
        while ai_idx < len(clip_paths) or user_idx < len(user_clips_paths):
            # Add AI clip
            if ai_idx < len(clip_paths):
                final_sequence_paths.append({'path': clip_paths[ai_idx], 'type': 'ai'})
                ai_idx += 1
            
            # Add User clip (if available and we haven't used all)
            if user_idx < len(user_clips_paths):
                final_sequence_paths.append({'path': user_clips_paths[user_idx], 'type': 'user'})
                user_idx += 1
                
        set_progress(80, "Stitching video clips and adding branding...")

        # 3. Create Video Base Clips
        clips = []
        for item in final_sequence_paths:
            p = item['path']
            is_user = (item['type'] == 'user')
            
            if os.path.exists(p):
                # Load clip
                # For User clips: Keep Audio (don't remove)
                # For AI clips: Keep Audio (Veo has audio)
                try:
                    c = VideoFileClip(p)
                    
                    # Resize/Crop to fill 9:16 (1080x1920)
                    # We accept that user clips might be reformatted
                    # If user clip is horizontal, we crop center
                    
                    c_resized = c.resize(height=h)
                    if c_resized.w < w:
                         c_resized = c_resized.resize(width=w)
                    c_final = c_resized.crop(x1=c_resized.w/2 - w/2, x2=c_resized.w/2 + w/2, y1=0, y2=h)
                    
                    # Trim user clips if they are too long (> 10s)?
                    # User request didn't specify, but let's keep pacing good.
                    # Max 8-10s per clip is reasonable for 'reels'
                    if is_user and c_final.duration > 10:
                        # Extract a random 8s chunk or first 8s?
                        # First 8s is safer to ensure context
                        c_final = c_final.subclip(0, 8)
                    elif not is_user:
                        # Ensure AI clips are exactly 8s (sometimes they vary slightly)
                         if c_final.duration > 8:
                            c_final = c_final.subclip(0, 8)
                            
                    clips.append(c_final)
                    
                except Exception as e:
                    print(f"Error processing clip {p}: {e}")

        if not clips:
            base_video = ColorClip(size=(w, h), color=(15, 23, 42), duration=total_duration)
        else:
            # Concatenate with method="compose" to handle different formats
            # We must ensure audio is preserved
            base_video = concatenate_videoclips(clips, method="compose")
            
            # Update total duration to actual length
            total_duration = base_video.duration


        # 4. Subtitles
        subtitle_clips = []
        if kwargs.get('subtitles', False):
            set_progress(85, "Generating auto-subtitles from audio...")
            try:
                # Extract audio to temporary file (Force Mono for Speech-to-Text)
                temp_audio_path = os.path.join(DIRS["temp"], f"temp_audio_{int(time.time())}.wav")
                base_video.audio.write_audiofile(
                    temp_audio_path, 
                    fps=44100, 
                    codec='pcm_s16le', 
                    ffmpeg_params=["-ac", "1"], 
                    verbose=False, 
                    logger=None
                )
                
                # Transcribe
                transcript = transcribe_audio_file(temp_audio_path)
                
                if transcript:
                    # Generate clips
                    subtitle_clips = generate_subtitle_clips(transcript, (w, h))
                    print(f"Generated {len(subtitle_clips)} subtitle clips.")
                else:
                    print("No speech detected or transcription failed.")
                
                # Cleanup temp audio
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    
            except Exception as e:
                print(f"Subtitle generation failed: {e}")
                # Continue without subtitles
                subtitle_clips = []

        # 5. Logo Overlay (Top Right - Small Area)
        # Persistent logo at Top Right
        if os.path.exists(LOGO_ICON):
            from PIL import Image
            # Load and convert to RGB to ensure compatibility
            logo_img = Image.open(LOGO_ICON).convert('RGB')
            logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
            logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(total_duration)
        else:
            logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=total_duration).set_opacity(0)


        # 6. Intro Scene (Branded)
        intro_duration = 1.5
        intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)  # Orange RGB
        
        if os.path.exists(LOGO_ICON):
            from PIL import Image
            logo_img = Image.open(LOGO_ICON).convert('RGB')
            intro_logo = ImageClip(np.array(logo_img)).resize(width=450).set_position('center').set_duration(intro_duration)
        else:
            intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)
        intro_text = TextClip(title.upper(), fontsize=70, color=BLACK, font=FONT_BOLD, size=(w-100, None), method='caption').set_position(('center', h/2 + 350)).set_duration(intro_duration)
        intro_scene = CompositeVideoClip([intro_bg, intro_logo, intro_text])

        # 7. Outro Scene (Branding at the end)
        outro_duration = 3.5
        outro_bg = ColorClip(size=(w, h), color=BLACK_RGB, duration=outro_duration)
        
        from PIL import Image
        outro_logo_img = Image.open(LOGO_ICON).convert('RGB')
        outro_logo = (ImageClip(np.array(outro_logo_img))
                      .resize(width=400)
                      .set_position('center')
                      .set_duration(outro_duration))
        
        outro_text = (TextClip("VirtualJobGuru\nYour Career. Your Growth.", 
                               fontsize=55, color=WHITE, font=FONT_BOLD, 
                               size=(w-100, None), method='caption')
                      .set_position(('center', h/2 + 300))
                      .set_duration(outro_duration))
        
        outro_composite = CompositeVideoClip([outro_bg, outro_logo, outro_text])

        # 8. Final Composite (Intro + Main Body + Outro)
        # Background for subtitles is optional if text has stroke, but let's keep a subtle gradient if needed
        # We'll use the subtitle_bg from before or just overlay on video
        
        main_elements = [base_video, logo_overlay] + subtitle_clips
        main_body = CompositeVideoClip(main_elements).set_duration(total_duration)
        
        final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])

        filename = f"branded_reel_{int(time.time())}.mp4"
        output_path = os.path.join(DIRS["video"], filename)
        
        set_progress(90, "Final rendering (this may take a minute)...")
        # Render with HIGH QUALITY settings
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec='libx264', 
            audio_codec='aac', 
            bitrate="8000k",  # Increased for better quality
            preset='medium',  # Better quality than ultrafast
            threads=4,
            logger=None,
            # Additional quality settings
            ffmpeg_params=[
                '-crf', '18',  # Constant Rate Factor (18 = high quality)
                '-pix_fmt', 'yuv420p',  # Compatibility
                '-movflags', '+faststart'  # Web streaming optimization
            ]
        )
        set_progress(100, "Done!", is_generating=False)
        
        return output_path, filename

    except Exception as e:
        import traceback
        print(f"Branded Video Error: {e}\n{traceback.format_exc()}")
        return None, str(e)

def create_extended_branded_video(script_text, title="Special Edition", visual_prompt=None, model_name="veo-3.1-generate-preview", api_key=None, project_id=None, **kwargs):
    """
    Creates a 30s+ video by generating one clip and extending it 3 times.
    Includes full branding, TTS, and consistency checks.
    """
    try:
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        w, h = 1080, 1920
        
        # 1. Generate Voiceover (TTS) first to know duration
        set_progress(5, "Generating voiceover...")
        audio_path, gender = generate_audio_speech(script_text)
        
        if audio_path:
            audio_clip = AudioFileClip(audio_path)
            script_duration = audio_clip.duration
        else:
            print("TTS failed, using default duration of 24s and silent audio.", flush=True)
            script_duration = 24.0
            audio_clip = None
        
        # 2. Generate initial 8s clip (Anchor Clip)
        set_progress(10, "Generating consistent anchor clip (Scene 1)...")
        # Ensure we have a high quality prompt
        anchor_prompt = f"{visual_prompt or 'A professional training session'}, professional vertical video, high resolution"
        anchor_path = generate_video_asset(anchor_prompt, project_id=p_id, model_name=model_name, api_key=api_key)
        
        if not anchor_path:
            return None, "Failed to generate anchor clip"
            
        final_clips = [anchor_path]
        current_video_duration = 8.0 # First clip is 8s
        
        # 3. Extensions loop to match script duration
        # Each extension is 7s. We need enough to cover script_duration + ~1s buffer
        max_extensions = 4 
        for i in range(max_extensions):
            if current_video_duration >= (script_duration + 1):
                break
                
            set_progress(20 + (i*15), f"Extending consistent scene (Part {i+2})...")
            # Logic: prompt for extension should emphasize continuity
            ext_prompt = f"Continued action, identical character and background, {visual_prompt or 'professional setting'}"
            ext_path = extend_video_asset(ext_prompt, final_clips[-1], project_id=p_id, model_name=model_name, api_key=api_key)
            
            if ext_path:
                final_clips.append(ext_path)
                current_video_duration += 7.0
            else:
                print(f"Extension {i+1} failed, but we have {len(final_clips)} clips.")
                break
        
        set_progress(75, "Assembling video scenes and mixing audio...")
        
        # Merge clips
        processed_clips = []
        for p in final_clips:
            c = VideoFileClip(p)
            c = c.resize(height=h)
            if c.w < w: c = c.resize(width=w)
            c = c.crop(x1=c.w/2 - w/2, x2=c.w/2 + w/2, y1=0, y2=h)
            processed_clips.append(c)
            
        main_body = concatenate_videoclips(processed_clips, method="compose")
        
        # Trim main body to match audio script
        if main_body.duration > script_duration:
            main_body = main_body.subclip(0, script_duration)
            
        # Add TTS and Music
        if audio_clip:
            main_body = main_body.set_audio(audio_clip)
        
        # 4. Add Branding (Intro + Outro)
        set_progress(85, "Adding intro and outro branding...")
        
        # Create Intro
        intro_path, _ = create_image_post(title, caption="AI GENERATED FOR YOU", show_branding=False)
        intro_scene = ImageClip(intro_path).set_duration(1.5).set_fps(30).crossfadein(0.5)
        
        # Create Outro
        outro_path, _ = create_image_post("THANK YOU", caption="Contact Virtual Job Guru", show_branding=True)
        outro_scene = ImageClip(outro_path).set_duration(3.5).set_fps(30).crossfadeout(0.5)
        
        # Mix with Background Music
        bg_music_path = os.path.join(ASSETS_DIR, "music/corporate_high_tech.mp3")
        if os.path.exists(bg_music_path):
            bg_music = AudioFileClip(bg_music_path).volumex(0.2).set_duration(intro_scene.duration + main_body.duration + outro_scene.duration)
            
            # Combine all audios
            audio_layers = [bg_music]
            if main_body.audio:
                audio_layers.append(main_body.audio.set_start(intro_scene.duration))
            
            final_audio = CompositeAudioClip(audio_layers)
        else:
            final_audio = main_body.audio.set_start(intro_scene.duration) if main_body.audio else None
            
        # Final Sequence
        final_video = concatenate_videoclips([intro_scene, main_body, outro_scene])
        final_video = final_video.set_audio(final_audio)
        
        # Add Logo Overlay on main body
        if os.path.exists(LOGO_ICON):
            logo_img = PIL.Image.open(LOGO_ICON).convert('RGB')
            logo_overlay = ImageClip(np.array(logo_img)).resize(width=180).set_opacity(0.8)
            logo_overlay = logo_overlay.set_position((w - 220, 60)).set_duration(final_video.duration)
            final_video = CompositeVideoClip([final_video, logo_overlay])

        # Render
        filename = f"extended_consistent_{int(time.time())}.mp4"
        output_path = os.path.join(DIRS["video"], filename)
        
        set_progress(95, "Rendering final consistent video...")
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec='libx264', 
            audio_codec='aac', 
            bitrate="8000k",
            ffmpeg_params=['-crf', '18', '-pix_fmt', 'yuv420p']
        )
        
        set_progress(100, "Done!", is_generating=False)
        return output_path, filename
        
    except Exception as e:
        import traceback
        print(f"Consistent Extension Error: {e}\n{traceback.format_exc()}")
        return None, str(e)

def create_hybrid_video(script_text, title="Hybrid Production", visual_prompt=None, project_id=None, **kwargs):
    """
    Intelligently mixes Library Assets with AI Generations.
    - Picks a category-matched video from the library.
    - Generates/Extends an AI clip for consistency.
    - Mixes audio & overlays auto-subtitles.
    """
    try:
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        w, h = 1080, 1920
        
        # 1. Load Assets from JSON
        json_path = '/root/.gemini/antigravity/scratch/social_automato/data/library_assets.json'
        if not os.path.exists(json_path):
            from index_assets import index_assets
            index_assets()
        
        with open(json_path, 'r') as f:
            assets = json.load(f)
            
        def fix_p(p):
            if p.startswith("/app/"):
                return p.replace("/app/", "/root/.gemini/antigravity/scratch/social_automato/")
            return p
        
        # 2. Pick a relevant "Hero" background video
        bg_video_path = None
        if assets.get("videos"):
            # Try to find a 'seminar' or 'coaching' video first
            preferred = [v for v in assets["videos"] if v.get('category') in ['seminar', 'coaching']]
            if not preferred: preferred = assets["videos"]
            
            if preferred:
                bg_asset = random.choice(preferred)
                bg_video_path = bg_asset['full_path']
                print(f"Selected Hybrid Asset: {bg_asset['name']} (Category: {bg_asset.get('category', 'unknown')})")
        
        # 3. Audio & Voice-over
        set_progress(10, "Generating voice-over...")
        audio_path, gender = generate_audio_speech(script_text)
        
        if not audio_path:
            print("Audio generation failed, using silence...")
            # Create a 5-second silence if audio fails
            from moviepy.config import get_setting
            ffmpeg_bin = get_setting("FFMPEG_BINARY")
            audio_path = os.path.join(DIRS["temp"], "silence.mp3")
            # Generate 5s of silence using ffmpeg
            silence_cmd = f"{ffmpeg_bin} -y -f lavfi -i anullsrc=r=44100:cl=mono -t 5 -q:a 9 -acodec libmp3lame {audio_path}"
            os.system(silence_cmd)
            
            # Mock transcription data for subtitles if TTS failed
            words = script_text.split()
            transcript_data = []
            for i, word in enumerate(words):
                 transcript_data.append({"word": word, "start": i*0.4, "end": (i+1)*0.4})
        else:
            # 6. Auto-Subtitles (Transcription)
            set_progress(60, "Transcribing audio for subtitles...")
            transcript_data = transcribe_audio_file(audio_path)
            if not transcript_data:
                print("Transcription yielded no results, trying mock...")
                words = script_text.split()
                transcript_data = [{"word": w, "start": i*0.4, "end": (i+1)*0.4} for i, w in enumerate(words)]
        
        audio_clip = AudioFileClip(audio_path)
        script_duration = audio_clip.duration
        
        # 4. Generate AI Foreground (Consistency Element)
        set_progress(30, "Generating AI Foreground Segment...")
        ai_prompt = f"{visual_prompt or 'Collaborative modern office, vertical video'}"
        ai_clip_path = generate_video_asset(ai_prompt, project_id=p_id)
        
        # 5. Composite Visuals
        set_progress(50, "Stitching Hybrid Visuals...")
        clips = []
        
        if ai_clip_path:
            ai_clip = VideoFileClip(ai_clip_path).resize(height=h)
            if ai_clip.w < w: ai_clip = ai_clip.resize(width=w)
            ai_clip = ai_clip.crop(x1=ai_clip.w/2 - w/2, x2=ai_clip.w/2 + w/2, y1=0, y2=h)
            
            # Determine segments: 50/50 split or adjusted to durations
            segment_duration = script_duration / 2
            clips.append(ai_clip.subclip(0, min(segment_duration, ai_clip.duration)))
        else:
            print("AI Foreground generation failed (Filtered or Error). Using library assets only.")
            segment_duration = script_duration # Use library for full length
        
        if bg_video_path:
            fixed_bg_path = fix_p(bg_video_path)
            print(f"DEBUG: Opening Background Clip: {fixed_bg_path}")
            bg_clip = VideoFileClip(fixed_bg_path).resize(height=h)
            if bg_clip.w < w: bg_clip = bg_clip.resize(width=w)
            bg_clip = bg_clip.crop(x1=bg_clip.w/2 - w/2, x2=bg_clip.w/2 + w/2, y1=0, y2=h)
            
            # Add second half from library (or full length if AI failed)
            if not clips:
                 clips.append(bg_clip.subclip(0, min(segment_duration, bg_clip.duration)))
            else:
                 clips.append(bg_clip.subclip(0, min(segment_duration, bg_clip.duration)))
        
        if not clips:
            return None, "No clips available (AI failed and no Library assets found)"
        
        base_video = concatenate_videoclips(clips, method="compose").set_audio(audio_clip)
        total_duration = base_video.duration

        # 6. Subtitles
        subtitle_clips = []
        if kwargs.get('subtitles', True): # Default to True for hybrid
            set_progress(70, "Generating auto-subtitles...")
            try:
                temp_audio_path = os.path.join(DIRS["temp"], f"temp_sub_{int(time.time())}.wav")
                audio_clip.write_audiofile(temp_audio_path, fps=16000, codec='pcm_s16le', ffmpeg_params=["-ac", "1"], verbose=False, logger=None)
                transcript = transcribe_audio_file(temp_audio_path)
                if transcript:
                    subtitle_clips = generate_subtitle_clips(transcript, (w, h))
                if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            except Exception as e:
                print(f"Subtitle Error: {e}")

        # 7. Final Branding
        final_elements = [base_video] + subtitle_clips
        
        # Add persistent logo if available
        if os.path.exists(LOGO_ICON):
            logo = ImageClip(LOGO_ICON).resize(width=180).set_position((w-220, 50)).set_duration(total_duration)
            final_elements.append(logo)
            
        final_composite = CompositeVideoClip(final_elements).set_duration(total_duration)
        
        filename = f"hybrid_branded_{int(time.time())}.mp4"
        output_path = os.path.join(DIRS["video"], filename)
        
        set_progress(90, "Rendering high quality final video...")
        final_composite.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', logger=None, threads=4)
        
        set_progress(100, "Hybrid Video Complete!", is_generating=False)
        return output_path, filename
    except Exception as e:
        import traceback
        print(f"Hybrid Error: {e}\n{traceback.format_exc()}")
        return None, str(e)

def analyze_video_asset(filename, project_id=None):
    """
    Uses Gemini to generate a short, punchy script for a Julia pickup clip
    based on the library asset's title and context.
    """
    try:
        # Get Gemini Key from env or config
        # For now, we simulate a robust analysis based on the filename
        # In a real scenario, this would call the Gemini API
        prompt = f"Analyze this professional HR video asset: {filename}. Generate a 1-sentence supportive tip that an HR expert named Julia would say as a follow-up. Keep it under 15 words."
        
        # Simulated Gemini Response mapping
        mapping = {
            "CV_Quick_Check": "Perfecting your CV is the first step to landing that dream role. Keep it clean and concise!",
            "Career_Coaching": "Investing in coaching is a game-changer for your long-term professional development. You've got this!",
            "Detailed_Resume": "A detailed resume tells your unique story. Make sure every word highlights your value.",
            "Interview_Preparation": "Preparation builds confidence. Always research the company culture before your big day!",
            "Seminar_50": "Learning is a lifelong journey. Use these insights to stay ahead in the evolving job market.",
            "Hiring_Older_Workers": "Diversity in experience is a huge asset. Don't underestimate the power of seasoned pros!"
        }
        
        for key, val in mapping.items():
            if key.lower() in filename.lower():
                return val
                
        return f"This overview of {filename.replace('_', ' ')} is essential for any career-minded professional. Stay focused!"
    except Exception as e:
        print(f"Analysis Error: {e}")
        return "Always keep growing and learning in your career journey!"

def create_library_remix_video(script_text, title="LIBRARY REMIX", visual_prompt=None, project_id=None, **kwargs):
    """
    Creates a 'Library Remix' video by combining a user asset, a branded thumbnail,
    a Julia AI 'pickup' commentary clip, and final branding.
    """
    try:
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        w, h = 1080, 1920
        timestamp = int(time.time())
        
        # 1. Select a Library Asset
        library_dir = "/app/generated_media/permanent/videos"
        if not os.path.exists(library_dir):
            library_dir = os.path.join(os.getcwd(), "generated_media/permanent/videos")
            
        video_files = [f for f in os.listdir(library_dir) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        if not video_files:
            return None, "No videos found in library"
            
        source_video_name = random.choice(video_files)
        source_video_path = os.path.join(library_dir, source_video_name)
        print(f"DEBUG: Selected Library Asset: {source_video_name}")
        
        set_progress(10, f"Selected asset: {source_video_name}")

        # 2. Analyze Asset (Gemini Logic)
        pickup_script = analyze_video_asset(source_video_name, project_id=p_id)
        print(f"DEBUG: Julia Pickup Script: {pickup_script}")
        
        # 3. Generate Julia 'Pickup' Clip (5s AI Video)
        set_progress(30, "Generating Julia pickup...")
        character = "A professional HR expert named Julia in a modern, high-end corporate office. She is wearing a sharp navy business suit, looking confident and approachable. Shot on ARRI Alexa, cinematic lighting."
        pickup_prompt = f"{character}, speaking directly to camera, nodding slightly, giving a brief tip: '{pickup_script}', professional and trustworthy, photorealistic 8k."
        
        pickup_gcs_path = f"gs://vjgu-video-generation/videos/pickup_{timestamp}.mp4"
        
        # Use GenAI Client (known to work)
        from google import genai
        from google.genai.types import GenerateVideosConfig
        client = genai.Client(vertexai=True, project=p_id, location="us-central1")
        
        print(f"Generating Julia pickup to {pickup_gcs_path}...")
        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-001",
            prompt=pickup_prompt,
            config=GenerateVideosConfig(
                aspect_ratio='9:16',
                output_gcs_uri=pickup_gcs_path
            )
        )
        
        while not operation.done:
            print("⏳ Generating Pickup...", flush=True)
            time.sleep(10)
            operation = client.operations.get(operation)
            
        if operation.result and operation.result.generated_videos:
             pickup_uri = operation.result.generated_videos[0].video.uri
             print(f"✅ Pickup generated: {pickup_uri}")
        else:
             return None, "Failed to generate Julia pickup"
             
        local_pickup_path = os.path.join(DIRS["video"], f"julia_pickup_{timestamp}.mp4")
        download_from_gcs(pickup_uri, local_pickup_path)
             
        # 4. Assembly
        set_progress(70, "Assembling remix...")
        
        # Helper to force RGB
        def ensure_rgb(clip, name="clip"):
            def _force_rgb(get_frame, t):
                frame = get_frame(t)
                if len(frame.shape) == 2:
                    return np.dstack([frame, frame, frame])
                elif frame.shape[2] == 4:
                    return frame[:,:,:3]
                return frame
            return clip.fl(_force_rgb)

        # Load clips
        asset_clip = VideoFileClip(source_video_path)
        # Resize/Crop asset to 9:16
        if asset_clip.w / asset_clip.h != w / h:
            asset_clip = asset_clip.resize(height=h)
            asset_clip = asset_clip.crop(x1=(asset_clip.w-w)/2, width=w, height=h)
        asset_clip = ensure_rgb(asset_clip, "asset")
            
        julia_clip = VideoFileClip(local_pickup_path)
        if julia_clip.w / julia_clip.h != w / h:
            julia_clip = julia_clip.resize(height=h)
            julia_clip = julia_clip.crop(x1=(julia_clip.w-w)/2, width=w, height=h)
        julia_clip = ensure_rgb(julia_clip, "julia")
        
        # Intro Scene (Branded Thumbnail Start)
        intro_duration = 2.0
        intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
        intro_bg = ensure_rgb(intro_bg, "intro_bg")
        intro_text = TextClip(title.upper(), fontsize=70, color='black', font='Montserrat-Bold', size=(w-100, None), method='caption').set_position(('center', 'center')).set_duration(intro_duration)
        intro_text = ensure_rgb(intro_text, "intro_text")
        intro_scene = CompositeVideoClip([intro_bg, intro_text])
        
        # Outro Scene
        outro_duration = 3.0
        outro_bg = ColorClip(size=(w, h), color=(0,0,0), duration=outro_duration)
        outro_bg = ensure_rgb(outro_bg, "outro_bg")
        outro_text = TextClip(f"VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color='white', font='Montserrat-Bold', size=(w-100, None), method='caption').set_position(('center', 'center')).set_duration(outro_duration)
        outro_text = ensure_rgb(outro_text, "outro_text")
        outro_composite = CompositeVideoClip([outro_bg, outro_text])
        
        # Combine everything
        # [Intro] -> [Asset] -> [Julia] -> [Outro]
        final_video = concatenate_videoclips([intro_scene, asset_clip, julia_clip, outro_composite])
        
        # Render
        final_filename = f"library_remix_{timestamp}.mp4"
        final_output_path = os.path.join(DIRS["video"], final_filename)
        
        set_progress(90, "Rendering final remix...")
        final_video.write_videofile(
            final_output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            bitrate="8000k",
            preset='medium',
            threads=4,
            logger=None
        )
        
        set_progress(100, "Done!", is_generating=False)
        return final_output_path, final_filename
        
    except Exception as e:
        import traceback
        print(f"Library Remix Error: {e}\n{traceback.format_exc()}")
        return None, str(e)

def download_from_gcs(uri, destination_path, project_id=None):
    """Downloads a file from Google Cloud Storage."""
    try:
        from google.cloud import storage
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        storage_client = storage.Client(project=p_id)
        
        parts = uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1]
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        blob.download_to_filename(destination_path)
        print(f"✅ Downloaded {uri} to {destination_path}")
        return True
    except Exception as e:
        print(f"GCS Download Error: {e}")
        return False

def create_complex_hybrid_video(script_text, title="Premium Production", visual_prompt=None, project_id=None, **kwargs):
    """
    Creates a high-quality 30s hybrid video with 4 distinct scenes using AI and Library assets.
    """
    try:
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        w, h = 1080, 1920
        # 1. Load Assets from JSON
        json_path = '/root/.gemini/antigravity/scratch/social_automato/data/library_assets.json'
        if not os.path.exists(json_path):
            from index_assets import index_assets
            index_assets()
        
        with open(json_path, 'r') as f:
            assets_data = json.load(f)
            
        def fix_p(p):
            if p.startswith("/app/"):
                return p.replace("/app/", "/root/.gemini/antigravity/scratch/social_automato/")
            return p

        print("Using Native Video Audio & Extensions for Consistency.")
        
        # 2. Generate Base AI Scene (Hook)
        set_progress(10, "Generating Base AI Scene...")
        p1 = "A professional female HR manager seating in a premium corporate office, cinematic lighting, vertical video, high resolution, talking to camera, audio included"
        base_path = generate_video_asset(p1, project_id=p_id, model_name="veo-3.1-generate-preview")
        
        if not base_path:
            return None, "Base generation failed."

        ai_clips = [base_path]
        
        # 3. Extend for Consistency (2 Extensions)
        # We want ~20s of AI footage. Base is ~7s. 2 extensions -> ~21s.
        current_last_path = base_path
        for i in range(2):
            set_progress(30 + (i*15), f"Extending Scene (Part {i+2})...")
            # Prompt must maintain context
            ext_prompt = "Continued speech, same character, same office, engaging gesture"
            ext_path = extend_video_asset(ext_prompt, current_last_path, project_id=p_id, model_name="veo-3.1-generate-preview")
            
            if ext_path:
                ai_clips = [ext_path] # Replace with extended version (cumulative)
                current_last_path = ext_path
            else:
                print(f"Extension {i+1} failed.")
                break

        # 4. Library Outro Selection
        video_list = assets_data.get('videos', [])
        # Prefer specific categories for outro
        outros = [v for v in video_list if v.get('category') in ['Coaching', 'Promotional', 'Testimonials']]
        if not outros: outros = video_list # Fallback to any video
        
        outro_meta = random.choice(outros) if outros else None

        # 5. Processing & Stitching
        set_progress(70, "Stitching Clips...")
        final_clips = []
        
        # Process AI Clips
        for path in ai_clips:
            try:
                clip = VideoFileClip(path).resize(height=h)
                if clip.w < w: clip = clip.resize(width=w)
                clip = clip.crop(x1=clip.w/2 - w/2, x2=clip.w/2 + w/2, y1=0, y2=h)
                final_clips.append(clip)
            except Exception as e:
                print(f"Error processing AI clip {path}: {e}")

        # Process Outro
        if outro_meta:
            try:
                op = fix_p(outro_meta['full_path'])
                oclip = VideoFileClip(op).resize(height=h)
                if oclip.w < w: oclip = oclip.resize(width=w)
                oclip = oclip.crop(x1=oclip.w/2 - w/2, x2=oclip.w/2 + w/2, y1=0, y2=h)
                # Cap outro at 5-8 seconds
                final_clips.append(oclip.subclip(0, min(8, oclip.duration)))
            except Exception as e:
                print(f"Error processing outro {op}: {e}")

        if not final_clips: return None, "Production failed: No clips generated"

        video_stream = concatenate_videoclips(final_clips, method="compose")
        print(f"Total Duration: {video_stream.duration}s")
        
        # 6. Overlays (Branding & Subtitles)
        set_progress(80, "Adding Branding & Subtitles...")
        
        # Logo (Top Right)
        logo_path = os.path.join(ASSETS_DIR, "logo/logo.png")
        if not os.path.exists(logo_path): logo_path = LOGO_ICON
        
        logo = ImageClip(logo_path).resize(width=220).set_position((w-260, 60)).set_duration(video_stream.duration).set_opacity(0.9)
        
        # Watermark (Bottom Left)
        watermark = TextClip("www.vjgu.online", fontsize=30, color='white', font='Montserrat-Regular').set_position((50, h-80)).set_duration(video_stream.duration).set_opacity(0.6)
        
        # Subtitles - Extract from Native Audio
        subtitle_clips = []
        try:
            if video_stream.audio:
                # Extract audio to temp file for transcription
                temp_audio = os.path.join(DIRS["temp"], f"native_audio_{int(time.time())}.mp3")
                if not hasattr(video_stream.audio, 'fps') or video_stream.audio.fps is None:
                    video_stream.audio.fps = 44100
                video_stream.audio.write_audiofile(temp_audio)
                
                transcript_data = transcribe_audio_file(temp_audio)
                if transcript_data:
                    subtitle_clips = generate_subtitle_clips(transcript_data, (w, h))
            else:
                 print("WARNING: Video has no native audio stream.")
        except Exception as e:
            print(f"Subtitle Generation Error: {e}")
        
        # Combine everything
        final_video = CompositeVideoClip([video_stream, logo, watermark] + subtitle_clips)
        
        filename = f"hr_mistakes_{int(time.time())}.mp4"
        output_path = os.path.join(DIRS["video"], filename)
        
        set_progress(90, "Rendering high-quality HR production...")
        final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', logger=None, threads=4)
        
        set_progress(100, "Production Complete!", is_generating=False)
        return output_path, filename

    except Exception as e:
        import traceback
        print(f"Complex Hybrid Error: {e}\n{traceback.format_exc()}")
        return None, str(e)

def create_image_post(title, caption=None, bg_path=None, show_branding=True, style='hero', custom_logo_path=None, visual_prompt=None, platform='instagram', aspect_ratio='portrait'):
    """
    Creates a high-quality branded image post using PIL for sharp text.
    aspect_ratio: 'square' (1:1), 'portrait' (4:5), 'vertical' (9:16)
    """
    try:
        # 1. Determine Dimensions
        if aspect_ratio == 'square':
            w, h = 1080, 1080
        elif aspect_ratio == 'vertical':
            w, h = 1080, 1920
        else: # Default: Portrait (4:5) - Best for Instagram/FB Feed
            w, h = 1080, 1350
        
        # Safe zones (15% margin)
        safe_x = int(w * 0.12)
        safe_y = int(h * 0.15)
        safe_w = w - (2 * safe_x)
        
        # Create base image
        if bg_path and os.path.exists(bg_path):
            img = PIL.Image.open(bg_path).convert('RGBA').resize((w, h), PIL.Image.Resampling.LANCZOS)
            # Darken overlay
            overlay = PIL.Image.new('RGBA', (w, h), (0, 0, 0, 110))
            img = PIL.Image.alpha_composite(img, overlay)
        else:
            img = PIL.Image.new('RGBA', (w, h), (30, 30, 30, 255))
            
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        if not os.path.exists(font_bold): font_bold = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"
        if not os.path.exists(font_reg): font_reg = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"

        draw = PIL.ImageDraw.Draw(img)

        # Style Logic
        next_y = safe_y
        if style == 'hero':
            # Title - Centered in safe zone
            title_y = int(h * 0.3)
            img, next_y = add_text_pil(img, title.upper(), ('center', title_y), font_bold, 80, WHITE_RGB, max_width=safe_w)
            
            # Caption
            if caption:
                caption_y = next_y + 40 # 40px gap
                img, next_y = add_text_pil(img, caption, ('center', caption_y), font_reg, 45, WHITE_RGB, max_width=safe_w)

        elif style == 'list':
            # Title
            img, next_y = add_text_pil(img, title, (safe_x, safe_y), font_bold, 70, WHITE_RGB, align='left', max_width=safe_w)
            
            sub_y = next_y + 30
            img, next_y = add_text_pil(img, "Key Takeaways:", (safe_x, sub_y), font_bold, 36, PRIMARY_ORANGE_RGB, align='left')
            
            points = [p.strip('- •').strip('123456789. ') for p in caption.split('\n') if p.strip()]
            py = next_y + 30
            for p in points[:6]:
                # Bullet
                draw.ellipse([safe_x, py+10, safe_x+20, py+30], fill=PRIMARY_ORANGE_RGB)
                img, py = add_text_pil(img, p, (safe_x+50, py), font_reg, 36, WHITE_RGB, max_width=safe_w-50, align='left')
                py += 20 # small extra gap between lines
            next_y = py

        # Branding
        if show_branding:
            # Footer Bar
            footer_h = int(h * 0.1) # 10% for footer
            draw.rectangle([0, h-footer_h, w, h], fill=BLACK_RGB)
            
            # Contact Text
            contact = "+49 1577 4331858  |  www.vjgu.online"
            img, _ = add_text_pil(img, contact, ('center', h - int(footer_h/2) - 15), font_reg, 28, WHITE_RGB)
            
            # Logo
            active_logo = custom_logo_path if (custom_logo_path and os.path.exists(custom_logo_path)) else LOGO_ICON
            if os.path.exists(active_logo):
                logo_size = int(h * 0.15) # Larger logo
                try:
                    logo = PIL.Image.open(active_logo).convert('RGBA')
                    logo.thumbnail((logo_size-30, logo_size-30))
                    
                    # White circle background for logo
                    box_x = w - logo_size - safe_x
                    box_y = h - footer_h - logo_size - 40 # Clear 40px gap above footer
                    draw.ellipse([box_x, box_y, box_x+logo_size, box_y+logo_size], fill=WHITE_RGB, outline=PRIMARY_ORANGE_RGB, width=3)
                    
                    # Paste logo
                    logo_x = box_x + (logo_size - logo.width) // 2
                    logo_y = box_y + (logo_size - logo.height) // 2
                    img.paste(logo, (logo_x, logo_y), logo)
                except Exception as e:
                    print(f"Logo Error: {e}")

        filename = f"{'branded' if show_branding else 'clean'}_post_{int(time.time())}.png"
        output_path = os.path.join(DIRS["image"], filename)
        img.save(output_path)
        return output_path, filename
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Branded Image PIL Error: {e}")
        return None, str(e)

def create_julia_ai_reels_video(script_text, title="CAREER SUCCESS SECRETS", visual_prompt=None, project_id=None, **kwargs):
    """
    Creates a consistent 'Senior HR Consultant' video using the extend_video method.
    This replaces the stitching method for automated posts.
    """
    try:
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        w, h = 1080, 1920
        
        # 1. Define Character & Prompts (Hardcoded for consistency as per user request)
        character = "A professional HR expert in a modern, high-end corporate office. She is wearing a sharp navy business suit, looking confident and approachable. The background is a blurred glass meeting room with warm, natural sunlight. Shot on ARRI Alexa, 85mm lens, cinematic lighting, photorealistic 8k, highly detailed texture."
        
        # Base Prompt
        base_prompt = f"{character}, speaking directly to camera giving expert career advice, subtle and natural hand gestures, maintaining strong eye contact, professional and trustworthy demeanor, high quality audio, crisp 4k video"
        
        # Extension Prompts
        extension_prompts = [
            f"{character}, continuing the explanation with passion, slight nod of agreement, same office setting, perfect continuity, engaging expression",
            f"{character}, emphasizing a critical point with hand movement, professional and articulate, consistent lighting and background, high resolution",
            f"{character}, wrapping up with an encouraging smile, friendly and supportive, same professional environment, cinematic depth of field"
        ]
        
        # 2. Generate Base Video
        set_progress(10, "Generating base 8s video (Veo 3)...")
        timestamp = int(time.time())
        # We need a GCS path for the base video to extend it
        bucket_name = "vjgu-video-generation" 
        base_gcs_path = f"gs://{bucket_name}/videos/auto_base_{timestamp}.mp4"
        
        # Import needed for direct generation
        from google import genai
        from google.genai.types import GenerateVideosConfig, Video
        
        client = genai.Client(vertexai=True, project=p_id, location=LOCATION)
        
        print(f"Generating base video to {base_gcs_path}...")
        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-001",
            prompt=base_prompt,
            config=GenerateVideosConfig(
                aspect_ratio='9:16',
                output_gcs_uri=base_gcs_path
            )
        )
        
        # Poll
        while not operation.done:
            print("⏳ Generating Base...", flush=True)
            time.sleep(10)
            operation = client.operations.get(operation)
            
        current_video_uri = None
        if operation.result and operation.result.generated_videos:
             current_video_uri = operation.result.generated_videos[0].video.uri
             print(f"✅ Base video generated: {current_video_uri}")
        else:
             return None, "Failed to generate base video"

        # 3. Extensions
        for i, ext_prompt in enumerate(extension_prompts, 1):
            set_progress(20 + (i*20), f"Extending video part {i}...")
            ext_gcs_path = f"gs://{bucket_name}/videos/auto_ext_{timestamp}_part{i}.mp4"
            
            print(f"Extending to {ext_gcs_path}...")
            op_ext = client.models.generate_videos(
                model="veo-3.1-fast-generate-001",
                prompt=ext_prompt,
                video=Video(
                    uri=current_video_uri,
                    mime_type="video/mp4"
                ),
                config=GenerateVideosConfig(
                    output_gcs_uri=ext_gcs_path
                )
            )
            
            while not op_ext.done:
                print(f"⏳ Extending {i}...", flush=True)
                time.sleep(10)
                op_ext = client.operations.get(op_ext)
            
            if op_ext.result and op_ext.result.generated_videos:
                current_video_uri = op_ext.result.generated_videos[0].video.uri
                print(f"✅ Extension {i} complete: {current_video_uri}")
            else:
                print(f"❌ Extension {i} failed.")
                break 

        # 4. Download Final Video
        set_progress(80, "Downloading final extended video...")
        
        # Parse GCS URI
        from google.cloud import storage
        parts = current_video_uri.replace("gs://", "").split("/", 1)
        dl_bucket_name = parts[0]
        dl_blob_path = parts[1]
        
        try:
            storage_client = storage.Client(project=p_id)
            bucket = storage_client.bucket(dl_bucket_name)
            blob = bucket.blob(dl_blob_path)
            
            raw_filename = f"raw_consistent_{timestamp}.mp4"
            raw_path = os.path.join(DIRS["temp"], raw_filename)
            blob.download_to_filename(raw_path)
        except Exception as e:
            print(f"Download Error: {e}")
            return None, "Download failed"
        
        # 5. Apply Branding
        set_progress(90, "Applying Branding...")
        
        # Load Video
        try:
            main_video = VideoFileClip(raw_path)
        except Exception as e:
            return None, f"Video load error: {e}"
            
        # Ensure 9:16
        if main_video.w != w or main_video.h != h:
             main_video = main_video.resize(height=h)
             if main_video.w < w: main_video = main_video.resize(width=w)
             main_video = main_video.crop(x1=(main_video.w-w)/2, width=w, height=h)
             
        # Helper to force RGB
        def ensure_rgb(clip, name="clip"):
            def _force_rgb(get_frame, t):
                frame = get_frame(t)
                # print(f"DEBUG: {name} frame shape: {frame.shape}")
                # If frame is grayscale (H, W), make it (H, W, 3)
                if len(frame.shape) == 2:
                    # print(f"DEBUG: {name} converting 2D to 3D")
                    return np.dstack([frame, frame, frame])
                # If frame is RGBA (H, W, 4), take RGB (H, W, 3)
                elif frame.shape[2] == 4:
                    return frame[:,:,:3]
                return frame
            return clip.fl(_force_rgb)

        # Apply to main video
        main_video = ensure_rgb(main_video, "main_video")
             
        total_duration = main_video.duration
        
        # Logo
        if os.path.exists(LOGO_ICON):
            logo_img = PIL.Image.open(LOGO_ICON).convert('RGB')
            logo_overlay = ImageClip(np.array(logo_img)).resize(width=150).set_opacity(0.9)
            logo_overlay = logo_overlay.set_position((w - 200, 60)).set_duration(total_duration)
            logo_overlay = ensure_rgb(logo_overlay, "logo_overlay")
        else:
            logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=total_duration).set_opacity(0)
            
        # Intro
        intro_duration = 1.5
        intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)
        intro_bg = ensure_rgb(intro_bg, "intro_bg")
        intro_text = TextClip(title.upper(), fontsize=70, color='black', font='Montserrat-Bold', size=(w-100, None), method='caption').set_position(('center', 'center')).set_duration(intro_duration)
        intro_text = ensure_rgb(intro_text, "intro_text")
        intro_scene = CompositeVideoClip([intro_bg, intro_text])
        
        # Outro
        outro_duration = 3.5
        outro_bg = ColorClip(size=(w, h), color=(0,0,0), duration=outro_duration) # Explicit tuple
        outro_bg = ensure_rgb(outro_bg, "outro_bg")
        outro_text = TextClip(f"VirtualJobGuru\nYour Career. Your Growth.", fontsize=55, color='white', font='Montserrat-Bold', size=(w-100, None), method='caption').set_position(('center', 'center')).set_duration(outro_duration)
        outro_text = ensure_rgb(outro_text, "outro_text")
        outro_composite = CompositeVideoClip([outro_bg, outro_text])
        
        # Combine
        try:
            final_elements = [main_video, logo_overlay]
            main_body = CompositeVideoClip(final_elements).set_duration(total_duration)
            # Ensure composites are also RGB?
            # intro_scene = ensure_rgb(intro_scene, "intro_scene")
            # main_body = ensure_rgb(main_body, "main_body")
            # outro_composite = ensure_rgb(outro_composite, "outro_composite")
            
            final_video = concatenate_videoclips([intro_scene, main_body, outro_composite])
        except Exception as e:
            return None, f"Composite Error: {e}"
        
        # Render
        final_filename = f"branded_consistent_{timestamp}.mp4"
        final_output_path = os.path.join(DIRS["video"], final_filename)
        
        set_progress(95, "Rendering final output...")
        final_video.write_videofile(
            final_output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            bitrate="8000k",
            preset='medium',
            threads=4,
            logger=None
        )
        
        set_progress(100, "Done!", is_generating=False)
        return final_output_path, final_filename
        
    except Exception as e:
        import traceback
        print(f"Consistent Video Error: {e}\n{traceback.format_exc()}")
        return None, str(e)
