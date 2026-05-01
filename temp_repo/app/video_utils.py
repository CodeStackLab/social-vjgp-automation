
import os
import subprocess
import json

def get_video_info(input_path):
    """Get video metadata using ffprobe"""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_streams', 
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
        return video_stream
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def convert_to_9_16(input_path, output_path=None):
    """
    Convert video to 9:16 aspect ratio (1080x1920) for Reels/TikTok.
    Strategies:
    - If already 9:16, just copy or re-encode if needed.
    - If landscape (16:9), crop to center 9:16 (Zoom/Crop).
    - Or add blurred background (Pillarbox) - Implementing Crop for now as it's better for full screen.
    """
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_9_16{ext}"
        
    try:
        info = get_video_info(input_path)
        if not info:
            return False, "Could not read video info"
            
        width = int(info.get('width', 0))
        height = int(info.get('height', 0))
        
        if width == 0 or height == 0:
            return False, "Invalid video dimensions"
            
        target_ratio = 9/16
        current_ratio = width / height
        
        print(f"[FFMPEG] Processing {input_path} ({width}x{height}) -> 9:16")
        
        # FFmpeg command builder
        cmd = ['ffmpeg', '-y', '-i', input_path]
        
        if abs(current_ratio - target_ratio) < 0.01:
            # Already close to 9:16, just verify resolution (e.g. 1080x1920)
            # We enforce 1080 width minimum for quality
            cmd.extend(['-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2'])
        else:
            # Crop logic: 
            # crop=h=ih:w=ih*(9/16) -> This takes center 9:16 part of image
            # Then scale to 1080x1920
            # Complex filter: scale to height 1920, then crop width to 1080
            
            # Better approach: scale to fill 1080x1920 (ZOOM to FILL)
            # scale=-1:1920 checks if width >= 1080. If not, scale=1080:-1
            
            vf_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            cmd.extend(['-vf', vf_filter])
            
        # Encoding settings for compatibility (H.264, AAC)
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg Error: {result.stderr}")
            return False, result.stderr
            
        return True, output_path
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        success, out = convert_to_9_16(sys.argv[1])
        print(f"Success: {success}, Output: {out}")
