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
    print('[INFO] Starting Direct Post Test...')
    
    # Path to media
    media_path = '/app/generated_media/temp/images/branded_post_1770644207.png'
    if not os.path.exists(media_path):
        import glob
        existing = glob.glob('/app/generated_media/temp/images/*.png')
        if existing: media_path = existing[-1]
        else:
            print('[ERROR] No images found.')
            sys.exit(1)

    print(f'[INFO] Using media: {media_path}')
    
    post_data = {
        'title': 'Final Connection Verification 🚀',
        'caption': 'All social platforms are abutely connected with REAL tokens! #Success #Verify #RealTokens',
        'platforms': ['facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'],
        'media_url': media_path,
        'type': 'image',
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    for p in post_data['platforms']:
        t = SOCIAL_TOKENS.get(p, {})
        is_real = not t.get('access_token', '').startswith('simulated_token')
        print(f'[INFO] {p}: {"REAL" if is_real else "FAKE"}')

    print('[INFO] Posting...')
    try:
        results = post_to_blotato(post_data)
        print('\n--- RESULTS ---')
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f'[ERROR] Posting failed: {str(e)}')
