
import os
import sys
import json
import time
import subprocess
import requests

# Add current directory to path
sys.path.append(os.getcwd())
import social_uploader
from video_utils import convert_to_9_16
from werkzeug.utils import secure_filename
import google.oauth2.credentials

def generate_unique_video():
    """Generates a unique 10-second video to avoid duplicate detection"""
    timestamp = int(time.time())
    output_path = f"/app/generated_media/temp/grand_test_{timestamp}.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate video with timestamp text
    # 16:9 Base
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', 'testsrc=duration=10:size=1920x1080:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=10',
        '-vf', f"drawtext=text='Social Automato Test {timestamp}':fontcolor=white:fontsize=64:box=1:boxcolor=black@0.5:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def run_final_post():
    print("\n" + "="*50)
    print("🚀 STARTING FINAL PUBLISH TO ALL PLATFORMS")
    print("="*50 + "\n")

    # 1. Generate Content
    print("[1/4] Generating unique video content...")
    base_video_path = generate_unique_video()
    print(f"✅ Generated 16:9 Video: {base_video_path}")
    
    # 2. Resize for Vertical Platforms
    print("[2/4] Optimizing for Vertical Platforms (IG/TikTok)...")
    success, vertical_video_path = convert_to_9_16(base_video_path)
    if success:
         print(f"✅ Generated 9:16 Video: {vertical_video_path}")
    else:
         print(f"❌ Resize Failed: {vertical_video_path}")
         vertical_video_path = base_video_path # Fallback
         
    # 3. Load Credentials
    print("[3/4] Loading credentials...")
    with open('/app/data/app_settings.json', 'r') as f:
        settings = json.load(f)
    tokens = settings.get('social_tokens', {})
    
    results = {}
    
    # 4. Publish Loop
    print("\n[4/4] Publishing...")
    
    # --- FACEBOOK (16:9) ---
    if 'facebook' in tokens:
        print("\n🔵 Posting to Facebook...")
        try:
            target = tokens['facebook']['pages'][0] # Use first page
            # FB Needs URL (served via nginx)
            rel_path = os.path.relpath(base_video_path, '/app/generated_media')
            media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
            
            resp = social_uploader.post_to_facebook(
                target['access_token'], target['id'], "Final System Test via API 🚀 #Automato", media_url
            )
            if resp.get('success'):
                results['Facebook'] = resp['url']
                print(f"✅ Success: {resp['url']}")
            else:
                results['Facebook'] = f"Failed: {resp.get('error')}"
                print(f"❌ Failed: {resp}")
        except Exception as e:
            results['Facebook'] = f"Error: {e}"
            
    # --- YOUTUBE (16:9) ---
    if 'youtube' in tokens:
        print("\n🔴 Posting to YouTube...")
        try:
            creds_data = tokens['youtube']
            creds = google.oauth2.credentials.Credentials(
                token=creds_data['access_token'],
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes')
            )
            resp = social_uploader.upload_video_youtube(
                creds, "Final System Test", "Automated Upload via Social Automato", base_video_path
            )
            if resp.get('success'):
                results['YouTube'] = resp['url']
                print(f"✅ Success: {resp['url']}")
            else:
                results['YouTube'] = f"Failed: {resp.get('error')}"
                print(f"❌ Failed: {resp}")
        except Exception as e:
            results['YouTube'] = f"Error: {e}"

    # --- LINKEDIN (16:9) ---
    if 'linkedin' in tokens:
        print("\n🔵 Posting to LinkedIn...")
        try:
            # LinkedIn needs URL
            rel_path = os.path.relpath(base_video_path, '/app/generated_media')
            media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
            
            resp = social_uploader.post_to_linkedin(
                tokens['linkedin']['access_token'], "Final System Test #Innovation", media_url
            )
            if resp.get('success'):
                results['LinkedIn'] = resp['url']
                print(f"✅ Success: {resp['url']}")
            elif resp.get('warning'):
                 results['LinkedIn'] = f"Warning: {resp['warning']} ({resp['url']})"
                 print(f"⚠️ Warning: {resp['warning']}")
            else:
                results['LinkedIn'] = f"Failed: {resp.get('error')}"
                print(f"❌ Failed: {resp}")
        except Exception as e:
            results['LinkedIn'] = f"Error: {e}"

    # --- INSTAGRAM (9:16) ---
    if 'instagram' in tokens and tokens.get('facebook', {}).get('pages'):
        print("\n🟣 Posting to Instagram...")
        try:
            # IG needs page token + IG Business ID
            # Find IG ID from FB pages
            page = tokens['facebook']['pages'][0]
            ig_id = page.get('instagram_business_account', {}).get('id')
            
            if ig_id:
                # Use Vertical Video URL
                rel_path = os.path.relpath(vertical_video_path, '/app/generated_media')
                media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
                
                resp = social_uploader.post_to_instagram(
                    page['access_token'], ig_id, "Final Vertical Test 📱 #Reels", media_url
                )
                if resp.get('success'):
                    results['Instagram'] = resp['url']
                    print(f"✅ Success: {resp['url']}")
                else:
                    results['Instagram'] = f"Failed: {resp.get('error')}"
                    print(f"❌ Failed: {resp}")
            else:
                results['Instagram'] = "Skipped: No IG Business Account linked to FB Page"
                print("⚠️ Skipped: No IG Business Account found")
        except Exception as e:
            results['Instagram'] = f"Error: {e}"

    # --- TIKTOK (9:16) ---
    if 'tiktok' in tokens:
        print("\n⚫ Posting to TikTok...")
        try:
            # Uses local vertical path
            resp = social_uploader.post_to_tiktok(
                tokens['tiktok']['access_token'], 
                tokens['tiktok'].get('open_id', 'me'),
                vertical_video_path,
                "Final Vertical Test #TikTok"
            )
            if resp.get('success'):
                results['TikTok'] = resp['url']
                print(f"✅ Success: {resp['url']}")
            else:
                results['TikTok'] = f"Failed: {resp.get('error')}"
                print(f"❌ Failed: {resp}")
        except Exception as e:
            results['TikTok'] = f"Error: {e}"
            
    # --- SUMMARY ---
    print("\n" + "="*50)
    print("📊 FINAL REPORT")
    print("="*50)
    for platform, result in results.items():
        print(f"👉 {platform}: {result}")
    
    # Write to file specific for user reading
    with open('/app/final_urls.txt', 'w') as f:
        for platform, result in results.items():
            f.write(f"{platform}: {result}\n")

if __name__ == "__main__":
    run_final_post()
