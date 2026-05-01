"""
Professional Video Generation Engine - OPTIMIZED VERSION
Generates client-ready 30-second videos in 3-5 minutes

Key Optimizations:
- Single 22-second Veo clip (instead of 5-6 clips)
- Photorealistic human prompts
- Auto-subtitles from audio
- Professional branding
"""

import os
import time
import textwrap
import json
from moviepy.editor import *
import moviepy.video.fx.all as vfx

# Import existing modules
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from google.cloud import speech
except ImportError:
    speech = None

from google.cloud import aiplatform, texttospeech
from google.oauth2 import service_account

# Configuration
ASSETS_DIR = "/app/assets"
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
OUTPUT_DIR = "/app/generated_media"
GCP_CREDS_PATH = "/app/google_credentials.json"
LOCATION = "us-central1"

# Brand Assets
PRIMARY_ORANGE = "#FF8D1F"
BLACK = "#000000"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F4F4F4"

FONT_BOLD = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
FONT_LIGHT = os.path.join(FONTS_DIR, "Montserrat-Light.ttf")

LOGO_ICON = os.path.join(ASSETS_DIR, "logo/logo.png")

DIRS = {
    "video": os.path.join(OUTPUT_DIR, "videos"),
    "image": os.path.join(OUTPUT_DIR, "images"),
    "temp": os.path.join(OUTPUT_DIR, "temp")
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


def init_vertex(credentials_json=None, project_id=None):
    """Initialize Vertex AI"""
    try:
        if credentials_json and len(str(credentials_json)) > 50:
            creds_dict = json.loads(credentials_json)
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            p_id = project_id or creds_dict.get('project_id')
            aiplatform.init(project=p_id, location=LOCATION, credentials=creds)
            return creds
        elif os.path.exists(GCP_CREDS_PATH):
            creds = service_account.Credentials.from_service_account_file(GCP_CREDS_PATH)
            aiplatform.init(project=project_id or os.getenv("GCP_PROJECT_ID"), location=LOCATION, credentials=creds)
            return creds
    except Exception as e:
        print(f"Vertex Init Error: {e}")
    return None


def generate_single_veo_clip(prompt: str, duration: int = 22, project_id: str = None) -> str:
    """
    Generate a SINGLE high-quality Veo clip with audio
    
    This is the KEY optimization - one long clip instead of multiple short clips
    Reduces generation time from 10+ minutes to 2-3 minutes
    """
    
    if not genai or not types:
        print("❌ google-genai not available")
        return None
    
    try:
        set_progress(10, "Initializing Veo 3.1 video generation...")
        
        # Get project ID
        p_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not p_id and os.path.exists(GCP_CREDS_PATH):
            with open(GCP_CREDS_PATH, 'r') as f:
                creds_dict = json.load(f)
                p_id = creds_dict.get('project_id')
        
        if not p_id:
            print("❌ No Project ID found!")
            return None
        
        # Initialize GenAI Client
        client = genai.Client(vertexai=True, project=p_id, location=LOCATION)
        
        print(f"🎬 Generating {duration}s Veo clip...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        set_progress(20, f"Requesting Veo generation ({duration}s clip)...")
        
        # Generate video
        # Note: Veo 3.1 generates audio by default, no need for with_audio parameter
        operation = client.models.generate_videos(
            model='veo-3.1-generate-preview',
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio='9:16',
                number_of_videos=1
            )
        )
        
        # Poll for completion (optimized polling)
        poll_count = 0
        max_polls = 100  # 5 minutes max (3s * 100)
        
        while not operation.done:
            poll_count += 1
            progress_percent = min(20 + (poll_count * 0.6), 80)  # 20% to 80%
            set_progress(int(progress_percent), f"Generating video... ({poll_count * 3}s elapsed)")
            
            if poll_count >= max_polls:
                print("⏱️ Timeout: Video generation took too long")
                return None
            
            print(f"⏳ Waiting... ({poll_count * 3}s)", flush=True)
            time.sleep(3)  # Optimized polling interval
        
        set_progress(85, "Video generated! Downloading...")
        
        # Get result
        result = operation.result()
        
        if not result.generated_videos:
            print("❌ No video generated")
            return None
        
        # Save video
        video_filename = f"veo_clip_{int(time.time()*1000)}.mp4"
        video_path = os.path.join(DIRS["temp"], video_filename)
        
        video_bytes = result.generated_videos[0].video.data
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        
        print(f"✅ Veo clip saved: {video_path}")
        set_progress(90, "Video downloaded successfully!")
        
        return video_path
        
    except Exception as e:
        print(f"❌ Veo Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def transcribe_audio_from_video(video_path: str) -> list:
    """
    Extract audio from video and transcribe using Google Cloud Speech-to-Text
    """
    
    if not speech:
        print("⚠️ google-cloud-speech not available, skipping transcription")
        return []
    
    try:
        set_progress(92, "Extracting audio for subtitles...")
        
        # Load video and extract audio
        video = VideoFileClip(video_path)
        
        if not video.audio:
            print("⚠️ No audio in video")
            return []
        
        # Extract audio as WAV
        temp_audio = os.path.join(DIRS["temp"], f"temp_audio_{int(time.time())}.wav")
        video.audio.write_audiofile(temp_audio, codec='pcm_s16le', fps=16000, logger=None)
        
        set_progress(94, "Transcribing audio...")
        
        # Transcribe
        client = speech.SpeechClient()
        
        with open(temp_audio, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_word_time_offsets=True,
            model="video"
        )
        
        response = client.recognize(config=config, audio=audio)
        
        # Extract word-level timestamps
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
        
        # Cleanup
        try:
            os.remove(temp_audio)
        except:
            pass
        
        print(f"✅ Transcribed {len(transcript_data)} words")
        return transcript_data
        
    except Exception as e:
        print(f"⚠️ Transcription error: {e}")
        return []


def generate_subtitle_clips(transcript_data: list, videosize: tuple, duration: float) -> list:
    """
    Generate karaoke-style subtitle clips from transcription
    """
    
    if not transcript_data:
        return []
    
    w, h = videosize
    clips = []
    
    # Group words into chunks of 3-4 words for readability
    chunk_size = 4
    for i in range(0, len(transcript_data), chunk_size):
        chunk = transcript_data[i:i+chunk_size]
        text = " ".join([w['word'] for w in chunk])
        start = chunk[0]['start']
        end = chunk[-1]['end']
        clip_duration = end - start
        
        if clip_duration < 0.5:
            clip_duration = 0.5
        
        # Ensure subtitle doesn't exceed video duration
        if start >= duration:
            break
        if end > duration:
            end = duration
            clip_duration = end - start
        
        # Create styled subtitle
        # Yellow text with black stroke (viral style)
        txt = (TextClip(
            text.upper(),
            fontsize=55,
            font=FONT_BOLD if os.path.exists(FONT_BOLD) else 'Arial-Bold',
            color='#FFD700',  # Gold/Yellow
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(w-100, None),
            align='center'
        )
        .set_position(('center', h - 350))
        .set_start(start)
        .set_duration(clip_duration))
        
        clips.append(txt)
    
    return clips


def create_professional_video(
    hook: str,
    main_script: str,
    cta: str,
    visual_prompt: str,
    title: str = "Career Tips",
    creds=None
) -> tuple:
    """
    Create a professional 30-second video optimized for speed and quality
    
    Target: 3-5 minutes total generation time
    
    Structure:
    - Intro: 3 seconds (branded)
    - Main: 22 seconds (single Veo clip with audio + subtitles)
    - Outro: 5 seconds (branded CTA)
    Total: 30 seconds
    
    Returns:
        (video_path, filename) or (None, error_message)
    """
    
    try:
        w, h = 1080, 1920
        
        set_progress(5, "Starting professional video generation...")
        
        # === INTRO (3 seconds) ===
        intro_duration = 3.0
        intro_bg = ColorClip(size=(w, h), color=(255, 141, 31), duration=intro_duration)  # Orange
        
        if os.path.exists(LOGO_ICON):
            intro_logo = (ImageClip(LOGO_ICON)
                         .resize(width=450)
                         .set_position('center')
                         .set_duration(intro_duration))
        else:
            intro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=intro_duration)
        
        # Hook text
        hook_text = (TextClip(
            hook.upper(),
            fontsize=70,
            color=BLACK,
            font=FONT_BOLD if os.path.exists(FONT_BOLD) else 'Arial-Bold',
            size=(w-100, None),
            method='caption',
            align='center'
        )
        .set_position(('center', h/2 + 350))
        .set_duration(intro_duration))
        
        intro_scene = CompositeVideoClip([intro_bg, intro_logo, hook_text])
        
        # === MAIN CONTENT (22 seconds) ===
        main_duration = 22.0
        
        # Generate single Veo clip
        p_id = os.getenv("GCP_PROJECT_ID")
        veo_path = generate_single_veo_clip(visual_prompt, duration=int(main_duration), project_id=p_id)
        
        if not veo_path or not os.path.exists(veo_path):
            return None, "Veo generation failed"
        
        # Load Veo clip
        main_video = VideoFileClip(veo_path)
        
        # Resize to 9:16
        main_video = main_video.resize(height=h)
        if main_video.w < w:
            main_video = main_video.resize(width=w)
        main_video = main_video.crop(x1=main_video.w/2 - w/2, x2=main_video.w/2 + w/2, y1=0, y2=h)
        
        # Set duration
        main_video = main_video.set_duration(main_duration)
        
        # Generate subtitles from audio
        transcript = transcribe_audio_from_video(veo_path)
        subtitle_clips = generate_subtitle_clips(transcript, (w, h), main_duration)
        
        # Fallback to script text if no subtitles
        if not subtitle_clips:
            print("⚠️ No subtitles generated, using fallback text")
            full_script = f"{hook} {main_script} {cta}"
            wrapped_text = "\\n".join(textwrap.wrap(full_script, width=32))
            
            fallback_subtitle = (TextClip(
                wrapped_text,
                fontsize=45,
                color=WHITE,
                font=FONT_BOLD if os.path.exists(FONT_BOLD) else 'Arial-Bold',
                size=(w-100, None),
                method='caption',
                align='center'
            )
            .set_position(('center', h - 350))
            .set_duration(main_duration))
            
            subtitle_clips = [fallback_subtitle]
        
        # Logo overlay (top-right, small)
        if os.path.exists(LOGO_ICON):
            logo_overlay = (ImageClip(LOGO_ICON)
                           .resize(width=120)
                           .set_opacity(0.8)
                           .set_position((w - 160, 60))
                           .set_duration(main_duration))
        else:
            logo_overlay = ColorClip(size=(1, 1), color=(0, 0, 0), duration=main_duration)
        
        # Composite main scene
        main_elements = [main_video, logo_overlay] + subtitle_clips
        main_scene = CompositeVideoClip(main_elements).set_duration(main_duration)
        
        # === OUTRO (5 seconds) ===
        outro_duration = 5.0
        outro_bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=outro_duration)  # Black
        
        if os.path.exists(LOGO_ICON):
            outro_logo = (ImageClip(LOGO_ICON)
                         .resize(width=400)
                         .set_position('center')
                         .set_duration(outro_duration))
        else:
            outro_logo = ColorClip(size=(1, 1), color=(0, 0, 0), duration=outro_duration)
        
        # CTA text
        cta_text = (TextClip(
            f"{cta}\\n\\nVirtualJobGuru\\nYour Career. Your Growth.",
            fontsize=55,
            color=WHITE,
            font=FONT_BOLD if os.path.exists(FONT_BOLD) else 'Arial-Bold',
            size=(w-100, None),
            method='caption',
            align='center'
        )
        .set_position(('center', h/2 + 300))
        .set_duration(outro_duration))
        
        outro_scene = CompositeVideoClip([outro_bg, outro_logo, cta_text])
        
        # === FINAL ASSEMBLY ===
        set_progress(96, "Assembling final video...")
        
        final_video = concatenate_videoclips([intro_scene, main_scene, outro_scene])
        
        # Render
        filename = f"professional_video_{int(time.time())}.mp4"
        output_path = os.path.join(DIRS["video"], filename)
        
        set_progress(98, "Rendering final video with HIGH QUALITY settings...")
        
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            bitrate="8000k",  # High quality bitrate
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
        
        set_progress(100, "Video generation complete!", is_generating=False)
        
        print(f"✅ Professional video created: {output_path}")
        
        return output_path, filename
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\\n{traceback.format_exc()}"
        print(f"❌ Video generation error: {error_msg}")
        set_progress(0, "Error occurred", is_generating=False)
        return None, error_msg


if __name__ == "__main__":
    # Test the professional video generator
    print("🎬 Testing Professional Video Generator\\n")
    
    test_hook = "Want to ace your next interview?"
    test_script = "Master these proven techniques that HR professionals actually look for."
    test_cta = "Follow for more career tips!"
    test_visual = "Photorealistic professional HR trainer, 30s woman in navy blazer, natural skin texture, confident eye contact, speaking to camera, modern corporate office with glass walls, natural lighting, 4K cinematic quality, real human features, NOT cartoon, NOT anime, NOT stylized"
    
    creds = init_vertex()
    
    video_path, filename = create_professional_video(
        hook=test_hook,
        main_script=test_script,
        cta=test_cta,
        visual_prompt=test_visual,
        title="Interview Tips",
        creds=creds
    )
    
    if video_path:
        print(f"\\n✅ SUCCESS!")
        print(f"📁 Path: {video_path}")
        print(f"🌐 URL: https://vjgu.online/videos/videos/{filename}")
    else:
        print(f"\\n❌ FAILED: {filename}")
