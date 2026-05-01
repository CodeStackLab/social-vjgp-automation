
import os
import sys
import json
import google.oauth2.credentials
import requests

# Add current directory to path
sys.path.append(os.getcwd())
import social_uploader

def test_live_posting():
    print("\n" + "="*50)
    print("STARTING LIVE POSTING TEST WITH TRUNCATION")

    print("="*50 + "\n")

    # 1. Load Real Credentials
    creds_path = r'C:\Users\mohda\.gemini\antigravity\scratch\app_settings.json'
    print(f"[1/3] Loading tokens from {creds_path}...")
    with open(creds_path, 'r') as f:
        settings = json.load(f)
    tokens = settings.get('social_tokens', {})

    # 2. Define LONG content
    long_title = "MASTERING YOUR CAREER: Why most people fail at interviews and how you can be the top 1% by following these simple but extremely effective strategies that I have learned over 10 years of coaching professionals in Berlin and worldwide. This title is intentionally made very long to test the automatic truncation logic that we have implemented to avoid YouTube and Facebook API rejections. If this post succeeds, it means our fix is working perfectly!"
    caption = "Stop failing interviews! 🚀 In this video, I share the secrets to career success. #CareerGrowth #InterviewTips #BerlinCoaching"
    
    # Existing test video
    media_path = r'C:\Users\mohda\.gemini\antigravity\scratch\social-automation\temp_repo\app\branded_reel_1769353709TEMP_MPY_wvf_snd.mp4'
    media_url = "https://www.w3schools.com/html/mov_bbb.mp4" # Sample for FB

    results = {}

    # 3. Test YouTube
    if 'youtube' in tokens:
        print("\nTesting YouTube Posting...")
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
                creds, long_title, caption, media_path
            )
            if resp.get('success'):
                results['YouTube'] = resp['url']
                print(f"YouTube Success: {resp['url']}")
            else:
                results['YouTube'] = f"Failed: {resp.get('error')}"
                print(f"YouTube Failed: {resp}")
        except Exception as e:
            results['YouTube'] = f"Error: {e}"
            print(f"YouTube Error: {e}")

    # 4. Test Facebook
    if 'facebook' in tokens:
        print("\nTesting Facebook Posting...")
        try:
            target = tokens['facebook']['pages'][0]
            resp = social_uploader.post_to_facebook(
                target['access_token'], target['id'], caption, media_url, title=long_title
            )
            if resp.get('success'):
                results['Facebook'] = resp['url']
                print(f"Facebook Success: {resp['url']}")
            else:
                results['Facebook'] = f"Failed: {resp.get('error')}"
                print(f"Facebook Failed: {resp}")
        except Exception as e:
            results['Facebook'] = f"Error: {e}"
            print(f"Facebook Error: {e}")

    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    for platform, result in results.items():
        print(f"👉 {platform}: {result}")

if __name__ == "__main__":
    test_live_posting()
