import sys
import os
sys.path.insert(0, '/app')
import time
import json

from main import app, post_to_blotato, SOCIAL_TOKENS, SMTP_SETTINGS

# Force SMTP disabled
SMTP_SETTINGS['enabled'] = False

with app.app_context():
    print('[INFO] Starting Video Post Test (Final)...')
    
    # Use the video file found earlier
    media_path = '/app/generated_media/temp/gen_clip_1770582517369.mp4'
    if not os.path.exists(media_path):
        print(f'[ERROR] Video not found at {media_path}')
        # Try finding another
        import glob
        existing = glob.glob('/app/generated_media/temp/*.mp4')
        if existing:
            media_path = existing[-1]
            print(f'[INFO] Found alternative video: {media_path}')
        else:
            print('[ERROR] No videos found anywhere.')
            sys.exit(1)

    post_data = {
        'title': 'Video Integration Validated 🎬',
        'caption': 'Final validation of video uploading capabilities. #Success #Video #Automation',
        'platforms': ['facebook', 'instagram', 'linkedin', 'youtube'], 
        'media_url': media_path,
        'type': 'video',
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f'[INFO] Posting to: {post_data["platforms"]}')
    try:
        results = post_to_blotato(post_data)
        print('\n--- RESULTS ---')
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f'[ERROR] Exception during posting: {e}')
