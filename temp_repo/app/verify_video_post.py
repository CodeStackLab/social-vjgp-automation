import sys
import os
sys.path.insert(0, '/app')
import time
import json

try:
    from main import app, post_to_blotato, SOCIAL_TOKENS, SMTP_SETTINGS
except Exception as e:
    print(f'[ERROR] Import failed: {str(e)}')
    sys.exit(1)

# Force SMTP disabled
SMTP_SETTINGS['enabled'] = False

with app.app_context():
    print('[INFO] Starting Video Post Test...')
    
    # Use a real video from temp (e.g. from the recent generation)
    import glob
    videos = glob.glob('/app/generated_media/temp/*.mp4')
    if not videos:
        print('[ERROR] No video clips found in temp. Trying perm.')
        videos = glob.glob('/app/generated_media/permanent/videos/*.mp4')
        
    if not videos:
        print('[ERROR] No videos found anywhere.')
        sys.exit(1)
        
    media_path = videos[-1]
    print(f'[INFO] Using video: {media_path}')
    
    post_data = {
        'title': 'YouTube Connection Test 📺',
        'caption': 'Success! YouTube integration verified with real video upload. #YouTube #Automation #Success',
        'platforms': ['linkedin', 'youtube'], # Only test those that support video well
        'media_url': media_path,
        'type': 'video',
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print('[INFO] Posting...')
    try:
        results = post_to_blotato(post_data)
        print('\n--- RESULTS ---')
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f'[ERROR] Posting failed: {str(e)}')
