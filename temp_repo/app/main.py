import os
import time
import requests
import threading
import json
import random
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from dotenv import load_dotenv
from functools import wraps
import video_engine
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import google.oauth2.credentials
import google_auth_oauthlib.flow
import social_uploader
from video_utils import convert_to_9_16

# Load configuration
load_dotenv()

# Fix for MoviePy/Pillow incompatibility: 'ANTIALIAS' was removed in Pillow 10
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-default")

import datetime
def get_germany_time():
    # Germany is UTC+1 in winter, UTC+2 in summer
    # We'll use a simple +1 offset for now as it's February
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Simple logic for German Winter Time (CET = UTC+1)
    return now_utc + datetime.timedelta(hours=1)

# Persistent Settings Storage
CONFIG_FILE = "/app/data/app_settings.json"
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

# Sample Media Storage
SAMPLES_DIR = "/app/assets/samples"
os.makedirs(SAMPLES_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mp3', 'wav', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Blotato & System Constants
# Blotato constants removed

PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "VJGU_Secure_Research_2026!@#")

# In-memory session data (Not persistent)
planner_queue = []
published_history = [] 
activity_logs = []
GENERATION_IN_PROGRESS = False
CURRENT_TASK = ""



# -------------------------------------------------------------------
# Bulk Schedule Queue Persistence
# -------------------------------------------------------------------
QUEUE_FILE = "/app/data/schedule_queue.json"
schedule_queue = []

def load_schedule_queue():
    """Load schedule queue from file"""
    global schedule_queue
    try:
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                schedule_queue = json.load(f)
                print(f"[QUEUE] Loaded {len(schedule_queue)} queued items")
    except Exception as e:
        print(f"[QUEUE ERROR] Failed to load: {e}")
        schedule_queue = []

def save_schedule_queue():
    """Save schedule queue to file"""
    try:
        os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
        with open(QUEUE_FILE, 'w') as f:
            json.dump(schedule_queue, f, indent=2)
    except Exception as e:
        print(f"[QUEUE ERROR] Failed to save: {e}")

# Load queue on startup
load_schedule_queue()

# AI Media Auto-Cleanup Configuration
TEMP_MEDIA_DIRS = [
    "/app/generated_media/temp",
    "/app/generated_media/temp/videos",
    "/app/generated_media/temp/images"
]
PERMANENT_MEDIA_DIRS = [
    "/app/generated_media/permanent/logos",
    "/app/generated_media/permanent/images",
    "/app/generated_media/permanent/videos",
    "/app/generated_media/permanent/pdfs"
]

def cleanup_old_ai_media():
    """Delete AI-generated media files older than 24 hours"""
    try:
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        deleted_count = 0
        
        for directory in TEMP_MEDIA_DIRS:
            # Extra safety: Never touch permanent directories
            if "/permanent" in directory:
                print(f"[CLEANUP SKIP] Safety trigger: Skipping permanent directory {directory}")
                continue

            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                continue
                
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Skip if not a file
                if not os.path.isfile(file_path):
                    continue
                    
                # Check file age
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"[CLEANUP] Deleted old AI media: {filename}")
                    except Exception as e:
                        print(f"[CLEANUP ERROR] Failed to delete {filename}: {e}")
        
        if deleted_count > 0:
            print(f"[CLEANUP] Successfully deleted {deleted_count} old AI media files")
        else:
            print("[CLEANUP] No old AI media files to delete")
            
    except Exception as e:
        print(f"[CLEANUP ERROR] Cleanup failed: {e}")

# Background scheduler disabled as requested
# scheduler = BackgroundScheduler()
# scheduler.add_job(cleanup_old_ai_media, 'interval', hours=1, id='cleanup_ai_media')
# scheduler.start()
# print("[SCHEDULER] AI media cleanup scheduler started (runs every hour)")

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Load settings
def load_persistent_settings():
    default_config = {
        "api_config": {
            "perplexity_key": os.getenv("PERPLEXITY_API_KEY", ""),
            "gemini_key": os.getenv("GEMINI_API_KEY", ""),
            "google_sheet_id": "",
            "video_model": "veo-3.1-fast-generate-001",
            "vertex_api_key": "YOUR_API_KEY",
            "vertex_project_id": "your-project-id"
        },
        "client_details": {
            "contact_info": {
                "phone": "+49 1577 4331858",
                "email": "info@virtualjobguru.com",
                "website": "www.virtualjobguru.com",
                "city": "Berlin, Germany",
                "custom_footer": "Link in Bio for 1-on-1 Coaching!"
            },
            "social_links": {
                "linkedin": "",
                "instagram": "@virtualjobguru",
                "tiktok": "@virtualjobguru",
                "youtube": "@virtualjobguru"
            },
            "branding": {
                "show_contact_in_video": True,
                "show_social_links": True,
                "overlay_position": "bottom"
            }
        },
        "blotato_config": {
            "api_base": "https://api.blotato.com/v1",
            "api_key": "",
            "channels": {
                "linkedin": "",
                "instagram": "",
                "tiktok": "",
                "youtube": "",
                "facebook": "" 
            }
        },
        "smtp_settings": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "app_password": "",
            "recipient_email": ""
        },
        "social_config": {
            "facebook": {"client_id": "", "client_secret": "", "auth_url": "https://www.facebook.com/v12.0/dialog/oauth", "doc_link": "https://developers.facebook.com/docs/facebook-login"},
            "instagram": {"client_id": "", "client_secret": "", "auth_url": "https://www.facebook.com/v12.0/dialog/oauth", "doc_link": "https://developers.facebook.com/docs/instagram-basic-display-api"},
            "linkedin": {"client_id": "", "client_secret": "", "auth_url": "https://www.linkedin.com/oauth/v2/authorization", "doc_link": "https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow"},
            "tiktok": {"client_id": "awal0unwa767ozk1", "client_secret": "xCnVhQi1ISD7wAAnXjVHPUdLukkSUoJr", "auth_url": "https://www.tiktok.com/v2/auth/authorize/", "doc_link": "https://developers.tiktok.com/doc/login-kit-web"},
            "youtube": {"client_id": "", "client_secret": "", "project_id": "", "auth_url": "https://accounts.google.com/o/oauth2/auth", "doc_link": "https://developers.google.com/youtube/v3/guides/uploading_a_video"}
        },
        "social_tokens": {
            "facebook": {"access_token": "", "status": "Disconnected"},
            "instagram": {"access_token": "", "status": "Disconnected"},
            "linkedin": {"access_token": "", "status": "Disconnected"},
            "tiktok": {"access_token": "", "status": "Disconnected"},
            "youtube": {"access_token": "", "status": "Disconnected"}
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                for k, v in saved.items():
                    if isinstance(v, dict) and k in default_config:
                        default_config[k].update(v)
                    else:
                        default_config[k] = v
                return default_config
        except:
            pass
    return default_config

def save_persistent_settings():
    data = {
        "api_config": API_CONFIG,
        "blotato_config": BLOTATO_CONFIG,
        "manual_posting_enabled": MANUAL_POSTING_ENABLED,
        "bulk_queue_enabled": BULK_QUEUE_ENABLED,
        "client_details": CLIENT_DETAILS,
        "smtp_settings": SMTP_SETTINGS,
        "social_config": SOCIAL_CONFIG,
        "social_tokens": SOCIAL_TOKENS
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize settings
SETTINGS = load_persistent_settings()
API_CONFIG = SETTINGS["api_config"]
BLOTATO_CONFIG = SETTINGS.get("blotato_config", {})
SMTP_SETTINGS = SETTINGS.get("smtp_settings", {})
MANUAL_POSTING_ENABLED = SETTINGS.get("manual_posting_enabled", False)
BULK_QUEUE_ENABLED = SETTINGS.get("bulk_queue_enabled", True)
CLIENT_DETAILS = SETTINGS.get("client_details", {})
SOCIAL_CONFIG = SETTINGS.get("social_config", {})
SOCIAL_TOKENS = SETTINGS.get("social_tokens", {})

# Bridge constants for backward compatibility
API_BASE = BLOTATO_CONFIG.get("api_base", "https://api.blotato.com/v1")
API_KEY = BLOTATO_CONFIG.get("api_key", "")
CHANNELS = BLOTATO_CONFIG.get("channels", {})

def add_log(action, level="INFO", details=""):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "action": action,
        "details": details
    }
    activity_logs.insert(0, log_entry)
    if len(activity_logs) > 100:
        activity_logs.pop()
    print(f"[{level}] {action}: {details}")

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html', date=datetime.datetime.now().strftime("%Y-%m-%d"))

@app.route('/terms')
def terms_of_service():
    return render_template('terms.html', date=datetime.datetime.now().strftime("%Y-%m-%d"))

@app.route('/tiktok-developers-site-verification.txt')
def tiktok_verify():
    return "tiktok-developers-site-verification=deSDfzY5lukuwprrLNxq7SNWP0RyQiAV"

@app.route('/tiktokdeSDfzY5lukuwprrLNxq7SNWP0RyQiAV')
def tiktok_verify_alt():
    return "tiktok-developers-site-verification=deSDfzY5lukuwprrLNxq7SNWP0RyQiAV"

@app.route('/tiktokdeSDfzY5lukuwprrLNxq7SNWP0RyQiAV.txt')
def tiktok_verify_alt_txt():
    return "tiktok-developers-site-verification=deSDfzY5lukuwprrLNxq7SNWP0RyQiAV"
# Auth Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            add_log("Login", "INFO", "Admin user logged in")
            return redirect(url_for('dashboard'))
        else:
            add_log("Login Failed", "WARNING", f"Failed attempt for {request.form['username']}")
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('index.html', domain=os.getenv('DOMAIN', 'vjgu.online'))

@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    global GENERATION_IN_PROGRESS, CURRENT_TASK
    status_data = {
        "generating": GENERATION_IN_PROGRESS,
        "task": CURRENT_TASK,
        "percent": 0
    }
    
    # Check for detailed progress file
    prog_file = "/app/data/gen_progress.json"
    if os.path.exists(prog_file):
        try:
            with open(prog_file, 'r') as f:
                detailed = json.load(f)
                # Only use if timestamp is recent (< 10 mins)
                if time.time() - detailed.get('timestamp', 0) < 600:
                    status_data.update(detailed)
        except: pass
        
    return jsonify(status_data)

@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    return jsonify(published_history)



@app.route('/api/queue', methods=['GET'])
@login_required
def get_queue():
    return jsonify(pending_posts)

@app.route('/api/queue/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_queue(post_id):
    if 0 <= post_id < len(pending_posts):
        pending_posts.pop(post_id)
        add_log("Queue", "INFO", f"Deleted post {post_id} from queue")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404



@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    return jsonify(activity_logs)

@app.route('/api/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    global activity_logs
    activity_logs = []
    add_log("System", "INFO", "Logs cleared")
    return jsonify({"status": "success"})



# API Configs (Already initialized from settings at top)
# Blotato route removed

@app.route('/api/settings/branding', methods=['GET', 'POST'])
@login_required
def manage_branding():
    global CLIENT_DETAILS
    if request.method == 'POST':
        data = request.json
        # Deep merge/update
        if 'contact_info' in data:
            CLIENT_DETAILS['contact_info'].update(data['contact_info'])
        save_persistent_settings()
        add_log("Settings", "INFO", "Branding & Profile updated")
        return jsonify({"status": "success"})
    return jsonify(CLIENT_DETAILS)




def get_random_logo():
    assets_dir = '/app/assets'
    logos = []
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')) and '__MACOSX' not in root:
                    logos.append(os.path.join(root, file))
    return random.choice(logos) if logos else None

@app.route('/api/bulk-create', methods=['POST'])
@login_required
def bulk_create():
    data = request.json
    posts = data.get('posts', [])
    for p in posts:
        planner_queue.append({
            "title": p.get('title'),
            "caption": p.get('caption'),
            "script": p.get('script'),
            "logo": p.get('logo'),
            "type": p.get('type', 'reel'), # Default to reel/video
            "visual_prompt": p.get('visual_prompt', ''),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    add_log("Bulk Planner", "INFO", f"Added {len(posts)} items to the Planner Queue")
    return jsonify({"status": "success"})

@app.route('/api/planner', methods=['GET'])
@login_required
def get_planner():
    return jsonify(planner_queue)

@app.route('/api/settings/toggle-auto', methods=['POST'])
@login_required
def toggle_auto():
    global AUTO_RESEARCH_ENABLED
    AUTO_RESEARCH_ENABLED = request.json.get('enabled', True)
    add_log("Settings", "INFO", f"Auto-Research: {AUTO_RESEARCH_ENABLED}")
    return jsonify({"status": "success"})

@app.route('/api/assets', methods=['GET'])
@login_required
def get_assets():
    assets_list = []
    
    # Include legacy /app/assets directory
    assets_dir = '/app/assets'
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), assets_dir)
                if '__MACOSX' not in rel_path:
                    assets_list.append({"name": file, "path": rel_path, "size": os.path.getsize(os.path.join(root, file))})
    
    # Include new permanent media directory
    permanent_dir = '/app/generated_media/permanent'
    if os.path.exists(permanent_dir):
        for root, dirs, files in os.walk(permanent_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, '/app/generated_media')
                if '__MACOSX' not in rel_path and not file.startswith('.'):
                    assets_list.append({"name": file, "path": rel_path, "size": os.path.getsize(full_path)})
    
    return jsonify(assets_list)

@app.route('/api/assets/upload', methods=['POST'])
@login_required
def upload_asset():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"status": "error", "message": "No file provided"}), 400

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
            category = 'logos' if 'logo' in filename.lower() else 'images'
        elif ext == 'pdf':
            category = 'pdfs'
        elif ext in ['mp4', 'mov', 'avi', 'webm', 'mkv', 'flv']:
            category = 'videos'
        else:
            category = 'images'  # default
        
        save_dir = f'/app/generated_media/permanent/{category}'
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, filename)
        file.save(save_path)
        
        # Ensure world-readable for serving
        os.chmod(save_path, 0o644)
        
        add_log("Upload", "INFO", f"Uploaded {filename} to {category}")
        return jsonify({"status": "success", "path": f"permanent/{category}/{filename}"})
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        add_log("Upload", "ERROR", f"Failed to upload: {str(e)}")
        print(error_trace)
        return jsonify({"status": "error", "message": str(e)}), 500
def upload_asset():
    file = request.files.get('file')
    if file:
        # Determine category based on file extension
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
            category = 'logos' if 'logo' in filename.lower() else 'images'
        elif ext == 'pdf':
            category = 'pdfs'
        elif ext in ['mp4', 'mov', 'avi', 'webm', 'mkv', 'flv']:
            category = 'videos'
        else:
            category = 'images'  # default
        
        save_path = os.path.join(f'/app/generated_media/permanent/{category}', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)
        add_log("Upload", "INFO", f"Uploaded {filename} to permanent/{category}")
        return jsonify({"status": "success", "path": f"permanent/{category}/{filename}"})
    return jsonify({"status": "error"}), 400

@app.route('/api/assets/delete', methods=['POST'])
@login_required
def delete_asset():
    path = request.json.get('path')
    if not path:
        return jsonify({"status": "error", "message": "No path provided"}), 400
        
    # Try multiple base directories for safety
    bases = ['/app/assets', '/app/generated_media']
    target_path = None
    
    for base in bases:
        test_path = os.path.normpath(os.path.join(base, path))
        if test_path.startswith(base) and os.path.exists(test_path):
            target_path = test_path
            break
            
    if target_path and os.path.isfile(target_path):
        try:
            os.remove(target_path)
            add_log("Delete", "WARNING", f"User deleted asset: {path}")
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "error", "message": "File not found or access denied"}), 400


@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('/app/generated_media', filename)




@app.route('/api/approve/<int:post_id>', methods=['POST'])
@login_required
def approve_post(post_id):
    if 0 <= post_id < len(pending_posts):
        post = pending_posts.pop(post_id)
        results = post_to_blotato(post)
        add_log("Publish", "INFO", str(results))
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404
@app.route('/api/settings/social-config', methods=['GET', 'POST'])
@login_required
def manage_social_config():
    global SOCIAL_CONFIG
    if request.method == 'POST':
        data = request.json
        print(f"[DEBUG] Received social config update: {data}")
        for platform in SOCIAL_CONFIG:
            if platform in data:
                print(f"[DEBUG] Updating {platform} with {data[platform]}")
                SOCIAL_CONFIG[platform].update(data[platform])
        save_persistent_settings()
        add_log("Settings", "INFO", "Social Developer API keys updated")
        return jsonify({"status": "success"})
    return jsonify(SOCIAL_CONFIG)

@app.route('/api/social/targets/select', methods=['POST'])
@login_required
def select_social_targets():
    """Select active pages/profiles for posting"""
    data = request.json
    platform = data.get('platform')
    target_ids = data.get('target_ids', [])
    
    if platform not in SOCIAL_TOKENS:
        return jsonify({"status": "error", "message": "Platform not connected"}), 400
        
    # Update selection status
    if "pages" in SOCIAL_TOKENS[platform]:
        for page in SOCIAL_TOKENS[platform]["pages"]:
            page["selected"] = page["id"] in target_ids
            
    save_persistent_settings()
    add_log("Settings", "INFO", f"Updated active targets for {platform}")
    return jsonify({"status": "success", "platform": platform, "targets": target_ids})

@app.route('/api/social/status', methods=['GET'])
@login_required
def get_social_status():
    return jsonify(SOCIAL_TOKENS)

@app.route('/api/social/auth/<platform>')
@login_required
def social_auth(platform):
    if platform not in SOCIAL_CONFIG:
        return "Invalid platform", 400
    
    config = SOCIAL_CONFIG[platform]
    if not config.get("client_id"):
        return f"Client ID for {platform} not configured", 400
    
    # redirect_uri = f"https://{request.host}/api/social/callback/{platform}"
    redirect_uri = f"https://vjgu.online/api/social/callback/{platform}"
    print(f"[REDIRECT DEBUG] Initial redirect_uri for {platform}: {redirect_uri}", flush=True)
    
    # YouTube / Google OAuth Flow
    if platform == 'youtube':
        client_config = {
            "web": {
                "client_id": config.get("client_id"),
                "client_secret": config.get("client_secret"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=[
                    'https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'openid'
                ]
            )
            flow.redirect_uri = redirect_uri
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            return redirect(authorization_url)
        except Exception as e:
            return f"Error initializing Google Auth: {str(e)}", 500

    # Standard OAuth redirect for other platforms
    auth_url = config.get("auth_url")
    params = {
        "client_id": config.get("client_id"),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": "random_secure_state"
    }

    # TikTok expects 'client_key', not 'client_id'
    if platform == 'tiktok':
        params["client_key"] = params.pop("client_id")
    print(f"[AUTH DEBUG] Platform: {platform}, Generated URI: {redirect_uri}")
    
    # Add scopes based on platform
    if platform == 'facebook':
        params["scope"] = "public_profile,email,pages_manage_posts,pages_read_engagement,pages_show_list,business_management"
    elif platform == 'instagram':
        params["scope"] = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"
    elif platform == 'linkedin':
        # UPDATED: Use modern scopes (r_liteprofile is deprecated)
        params["scope"] = "openid profile email w_member_social"
    elif platform == 'tiktok':
        # FORCE V2 Authorize URL
        auth_url = "https://www.tiktok.com/v2/auth/authorize/"
        print(f"[TIKTOK DEBUG] auth_url set to: {auth_url}", flush=True)
        print(f"[TIKTOK DEBUG] redirect_uri BEFORE override: {params.get('redirect_uri')}", flush=True)
        # Use ONLY the basic scope that should be approved by default
        params["scope"] = "user.info.basic,video.upload"
        # TikTok expects 'client_key', not 'client_id'
        # FORCE CLEAN REDIRECT URI just in case
        params["redirect_uri"] = "https://vjgu.online/api/social/callback/tiktok"
        # TikTok DOES NOT SUPPORT state parameter in the way other platforms do
        # Remove it to prevent TikTok from appending it to redirect_uri
        params.pop("state", None)
        print(f"[TIKTOK DEBUG] redirect_uri AFTER override: {params.get('redirect_uri')}", flush=True)
        print(f"[TIKTOK DEBUG] Full params dict: {params}", flush=True)
    # Use proper URL encoding
    from urllib.parse import urlencode
    query = urlencode(params)
    # query = "&".join([f"{k}={v}" for k, v in params.items()])
    final_url = f"{auth_url}?{query}"
    print(f"[FINAL URL] Redirecting to: {final_url}", flush=True)
    return redirect(final_url)

@app.route('/api/social/callback/<platform>')
def social_callback(platform):
    # Log all parameters for debugging
    print(f"[AUTH DEBUG] Callback for {platform}. Params: {request.args}")
    
    code = request.args.get('code')
    error = request.args.get('error')
    error_desc = request.args.get('error_description')
    
    if error:
        add_log("Social Auth", "ERROR", f"{platform} connection failed: {error} - {error_desc}")
        return f"<h1>Authorization Failed via {platform}</h1><p>Error: {error}</p><p>Description: {error_desc}</p>", 400
        
    if not code:
        return f"<h1>Authorization Failed</h1><p>No code provided by {platform}.</p><p>Debug info: {request.args}</p>", 400
    
    config = SOCIAL_CONFIG.get(platform)
    if not config:
        return "Invalid platform", 400

    redirect_uri = f"https://{request.host}/api/social/callback/{platform}"
    
    # YouTube / Google OAuth Callback
    if platform == 'youtube':
        try:
            client_config = {
                "web": {
                    "client_id": config.get("client_id"),
                    "client_secret": config.get("client_secret"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            }
            
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=[
                    'https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'openid'
                ],
                state=request.args.get('state')
            )
            flow.redirect_uri = redirect_uri
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            SOCIAL_TOKENS[platform] = {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "status": "Connected",
                "connected_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_persistent_settings()
            add_log("Social Auth", "SUCCESS", f"Connected to YouTube")
            
            return """
            <html>
            <head><style>body { font-family: sans-serif; text-align: center; padding: 50px; background: #0b0f1a; color: white; }</style></head>
            <body>
                <h1 style="color: #ff0000;">▶️ YouTube Connected!</h1>
                <p>Your account has been connected. You can close this window now.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
            </html>
            """
        except Exception as e:
            add_log("Social Auth", "ERROR", f"YouTube exchange failed: {str(e)}")
            return f"<h1>YouTube Connection Failed</h1><p>Error: {str(e)}</p>", 500

    # TikTok V2 Token Exchange
    if platform == 'tiktok':
        try:
            token_url = "https://open.tiktokapis.com/v2/oauth/token/"
            token_data = {
                "client_key": config.get("client_id"),
                "client_secret": config.get("client_secret"),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://vjgu.online/api/social/callback/tiktok"
            }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            # Using urllib.parse to encode data for x-www-form-urlencoded
            from urllib.parse import urlencode
            r = requests.post(token_url, data=urlencode(token_data), headers=headers)
            resp = r.json()
            
            if 'access_token' in resp:
                SOCIAL_TOKENS[platform] = {
                    "access_token": resp['access_token'],
                    "refresh_token": resp.get('refresh_token'),
                    "open_id": resp.get('open_id'),
                    "status": "Connected",
                    "connected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pages": [{"id": "me", "name": "TikTok Profile", "type": "profile", "selected": True}]
                }
                save_persistent_settings()
                add_log("Social Auth", "SUCCESS", f"Connected to TikTok")
                
                return f"""
                <html>
                <head><style>body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #0b0f1a; color: white; }}</style></head>
                <body>
                    <div style="font-size: 5rem; margin-bottom: 20px;">🎵</div>
                    <h1 style="color: #00f2ea;">TikTok Connected!</h1>
                    <p>Your account has been connected. You can close this window now.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body>
                </html>
                """
            else:
                add_log("Social Auth", "ERROR", f"TikTok exchange failed: {resp}")
                return f"<h1>TikTok Connection Failed</h1><p>Error: {resp.get('error_description', resp.get('error', 'Unknown Error'))}</p>", 400
                
        except Exception as e:
            add_log("Social Auth", "ERROR", f"TikTok exception: {str(e)}")
            return f"<h1>TikTok Connection Exception</h1><p>{str(e)}</p>", 500

    # FACEBOOK OAUTH - Real Implementation
    if platform == 'facebook':
        try:
            config = SOCIAL_CONFIG.get('facebook', {})
            
            # Try both 'app_id' and 'client_id' for compatibility
            client_id = config.get('app_id') or config.get('client_id')
            client_secret = config.get('app_secret') or config.get('client_secret')
            
            if not client_id or not client_secret:
                add_log("Social Auth", "ERROR", "Facebook: Missing app_id or app_secret in config")
                return "<h1>Facebook Connection Failed</h1><p>Error: Missing Facebook app credentials. Please configure app_id and app_secret.</p>", 400
            
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': 'https://vjgu.online/api/social/callback/facebook',
                'code': code
            }
            
            r = requests.get(token_url, params=params)
            token_data = r.json()
            
            if 'access_token' not in token_data:
                add_log("Social Auth", "ERROR", f"Facebook token exchange failed: {token_data}")
                return f"<h1>Facebook Connection Failed</h1><p>Error: {token_data.get('error', {}).get('message', 'Unknown error')}</p>", 400
            
            short_token = token_data['access_token']
            
            # Exchange for long-lived token (60 days)
            long_token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            long_params = {
                'grant_type': 'fb_exchange_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'fb_exchange_token': short_token
            }
            
            r2 = requests.get(long_token_url, params=long_params)
            long_token_data = r2.json()
            access_token = long_token_data.get('access_token', short_token)
            
            # Get user's pages
            pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
            pages_r = requests.get(pages_url, params={'access_token': access_token})
            pages_data = pages_r.json()
            
            print(f"[FACEBOOK DEBUG] Pages response: {pages_data}")
            add_log("Social Auth", "DEBUG", f"Facebook Pages count: {len(pages_data.get('data', []))}")
            
            pages = []
            for page in pages_data.get('data', []):
                pages.append({
                    'id': page['id'],
                    'name': page['name'],
                    'access_token': page['access_token'],
                    'type': 'page',
                    'selected': len(pages) == 0
                })
            
            if not pages:
                pages.append({'id': 'me', 'name': 'My Profile', 'type': 'profile', 'selected': True})
            
            SOCIAL_TOKENS['facebook'] = {
                'access_token': access_token,
                'status': 'Connected',
                'connected_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'pages': pages
            }
            save_persistent_settings()
            add_log("Social Auth", "SUCCESS", f"Connected to Facebook with {len(pages)} page(s)")
            
            return f"""<html><head><style>body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #f0f2f5; color: #1c1e21; }}</style></head><body><div style="font-size: 5rem; margin-bottom: 20px;">✅</div><h1 style="color: #1877f2;">Facebook Connected!</h1><p>Successfully connected {len(pages)} page(s).</p><script>setTimeout(() => window.close(), 3000);</script></body></html>"""
        except Exception as e:
            add_log("Social Auth", "ERROR", f"Facebook exception: {str(e)}")
            return f"<h1>Facebook Connection Exception</h1><p>{str(e)}</p>", 500

    # INSTAGRAM OAUTH - Real Implementation
    elif platform == 'instagram':
        try:
            # Instagram uses Facebook OAuth, but config might have different key names
            fb_config = SOCIAL_CONFIG.get('facebook', {})
            ig_config = SOCIAL_CONFIG.get('instagram', {})
            
            # Try both 'app_id' and 'client_id' for compatibility
            client_id = fb_config.get('app_id') or fb_config.get('client_id') or ig_config.get('client_id') or ig_config.get('app_id')
            client_secret = fb_config.get('app_secret') or fb_config.get('client_secret') or ig_config.get('client_secret') or ig_config.get('app_secret')
            
            if not client_id or not client_secret:
                add_log("Social Auth", "ERROR", "Instagram: Missing client_id or client_secret in config")
                return "<h1>Instagram Connection Failed</h1><p>Error: Missing Facebook app credentials. Please configure Facebook app_id and app_secret.</p>", 400
            
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': 'https://vjgu.online/api/social/callback/instagram',
                'code': code
            }
            
            r = requests.get(token_url, params=params)
            token_data = r.json()
            
            if 'access_token' not in token_data:
                add_log("Social Auth", "ERROR", f"Instagram token exchange failed: {token_data}")
                return f"<h1>Instagram Connection Failed</h1><p>Error: {token_data.get('error', {}).get('message', 'Unknown error')}</p>", 400
            
            access_token = token_data['access_token']
            
            pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
            pages_r = requests.get(pages_url, params={'access_token': access_token})
            pages_data = pages_r.json()
            
            instagram_accounts = []
            for page in pages_data.get('data', []):
                ig_url = f"https://graph.facebook.com/v18.0/{page['id']}"
                ig_r = requests.get(ig_url, params={'fields': 'instagram_business_account', 'access_token': page['access_token']})
                ig_data = ig_r.json()
                
                print(f"[INSTAGRAM DEBUG] Page {page['id']} ({page['name']}) IG response: {ig_data}")
                
                if 'instagram_business_account' in ig_data:
                    ig_id = ig_data['instagram_business_account']['id']
                    instagram_accounts.append({
                        'id': ig_id,
                        'name': f"Instagram ({page['name']})",
                        'access_token': page['access_token'],
                        'type': 'instagram_business',
                        'selected': True
                    })
            
            if not instagram_accounts:
                instagram_accounts.append({'id': 'none', 'name': 'No Instagram Business Account', 'type': 'none', 'selected': False})
            
            SOCIAL_TOKENS['instagram'] = {
                'access_token': access_token,
                'status': 'Connected',
                'connected_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'accounts': instagram_accounts
            }
            save_persistent_settings()
            add_log("Social Auth", "SUCCESS", f"Connected to Instagram with {len(instagram_accounts)} account(s)")
            
            return f"""<html><head><style>body {{ font-family: sans-serif; text-align: center; padding: 50px; background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); color: white; }}</style></head><body><div style="font-size: 5rem; margin-bottom: 20px;">✅</div><h1>Instagram Connected!</h1><p>Successfully connected {len(instagram_accounts)} account(s).</p><script>setTimeout(() => window.close(), 3000);</script></body></html>"""
        except Exception as e:
            add_log("Social Auth", "ERROR", f"Instagram exception: {str(e)}")
            return f"<h1>Instagram Connection Exception</h1><p>{str(e)}</p>", 500

    # LINKEDIN OAUTH - Real Implementation
    elif platform == 'linkedin':
        try:
            config = SOCIAL_CONFIG.get('linkedin', {})
            
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://vjgu.online/api/social/callback/linkedin',
                'client_id': config.get('client_id'),
                'client_secret': config.get('client_secret')
            }
            
            r = requests.post(token_url, data=data)
            token_data = r.json()
            
            if 'access_token' not in token_data:
                add_log("Social Auth", "ERROR", f"LinkedIn token exchange failed: {token_data}")
                return f"<h1>LinkedIn Connection Failed</h1><p>Error: {token_data.get('error_description', 'Unknown error')}</p>", 400
            
            access_token = token_data['access_token']
            
            profile_url = "https://api.linkedin.com/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_r = requests.get(profile_url, headers=headers)
            profile_data = profile_r.json()
            
            pages = [{'id': profile_data.get('sub', 'me'), 'name': profile_data.get('name', 'Personal Profile'), 'type': 'profile', 'selected': True}]
            
            try:
                orgs_url = "https://api.linkedin.com/v2/organizationAcls"
                orgs_r = requests.get(orgs_url, headers=headers, params={'q': 'roleAssignee'})
                orgs_data = orgs_r.json()
                for org in orgs_data.get('elements', []):
                    org_id = org.get('organization', '').split(':')[-1]
                    if org_id:
                        pages.append({'id': org_id, 'name': f"Organization {org_id}", 'type': 'organization', 'selected': False})
            except:
                pass
            
            SOCIAL_TOKENS['linkedin'] = {
                'access_token': access_token,
                'status': 'Connected',
                'connected_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                'pages': pages
            }
            save_persistent_settings()
            add_log("Social Auth", "SUCCESS", f"Connected to LinkedIn")
            
            return f"""<html><head><style>body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #0A66C2; color: white; }}</style></head><body><div style="font-size: 5rem; margin-bottom: 20px;">✅</div><h1>LinkedIn Connected!</h1><p>Successfully connected to your profile.</p><script>setTimeout(() => window.close(), 3000);</script></body></html>"""
        except Exception as e:
            add_log("Social Auth", "ERROR", f"LinkedIn exception: {str(e)}")
            return f"<h1>LinkedIn Connection Exception</h1><p>{str(e)}</p>", 500

    # Generic/Simulation OAuth Callback for others (fallback)
    access_token = "simulated_token_" + code[:10]
    pages = []
    
    SOCIAL_TOKENS[platform] = {
        "access_token": access_token,
        "status": "Connected",
        "connected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages": pages
    }
    
    save_persistent_settings()
    add_log("Social Auth", "SUCCESS", f"Connected to {platform}")
    
    return """
    <html>
    <head><style>body { font-family: sans-serif; text-align: center; padding: 50px; background: #0b0f1a; color: white; }</style></head>
    <body>
        <h1 style="color: #10b981;">✅ Connection Successful!</h1>
        <p>Your account has been connected. You can close this window now.</p>
        <script>setTimeout(() => window.close(), 3000);</script>
    </body>
    </html>
    """





@app.route('/api/settings/blotato', methods=['GET', 'POST'])
@login_required
def manage_blotato():
    global BLOTATO_CONFIG, API_BASE, API_KEY, CHANNELS
    if request.method == 'POST':
        BLOTATO_CONFIG.update(request.json)
        # Update bridge constants
        API_BASE = BLOTATO_CONFIG.get("api_base", "https://api.blotato.com/v1")
        API_KEY = BLOTATO_CONFIG.get("api_key", "")
        CHANNELS = BLOTATO_CONFIG.get("channels", {})
        save_persistent_settings()
        add_log("Settings", "INFO", "Blotato API settings updated")
        return jsonify({"status": "success"})
    return jsonify(BLOTATO_CONFIG)





def post_to_blotato(post_data):
    """Post to social platforms"""
    url = f"{API_BASE}/posts"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    results = []
    media_url = post_data.get('media_url')
    if media_url and not media_url.startswith("http"):
        # Correctly resolve relative path for public URL
        if '/app/generated_media/' in media_url:
            rel_path = media_url.split('/app/generated_media/')[-1]
            media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
        else:
            media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{os.path.basename(media_url)}"
    
    platforms_posted = []
    target_platforms = post_data.get('platforms', list(CHANNELS.keys()))
    for p in target_platforms:
        cid = CHANNELS.get(p)
        if not cid: continue
        
        # Apply truncation here as well (secondary defense)
        raw_caption = post_data.get('caption', '')
        raw_title = post_data.get('title', '')
        
        safe_caption = raw_caption[:2000] # Safe limit for most platforms
        safe_title = raw_title
        
        if p == 'youtube': safe_title = raw_title[:100]
        elif p == 'facebook': safe_title = raw_title[:255]
        
        # V2 Blotato Post Structure
        payload = {
            "post": {
                "accountId": cid,
                "content": {
                    "text": safe_caption,
                    "title": safe_title,
                    "mediaUrls": [media_url] if media_url else []
                }
            }
        }
        # In this implementation, it doesn't seem to actually send 'payload' to Blotato API yet,
        # but if it did, it would be safe now.

    # DIRECT SOCIAL MEDIA POSTING
    print(f"[SOCIAL PUBLISH] Processing {target_platforms} for: {post_data.get('title', 'Untitled')}")
    
    # In a real scenario, we would iterate through platforms and their selected targets
    results = {}
    platforms_posted = []

    try:
        for platform in target_platforms:
            platform = platform.lower()
            if platform not in SOCIAL_TOKENS:
                print(f"[SOCIAL PUBLISH] Skipping {platform} (Not connected)")
                continue
                
            token_data = SOCIAL_TOKENS[platform]
            
            # Determine targets (Profile + Pages)
            # Determine targets (Profile + Pages)
            targets = []
            
            # Check for specific target override
            specific_target_id = post_data.get('target_id')
            
            if "pages" in token_data:
                # Multi-target support (Facebook, LinkedIn)
                if specific_target_id:
                    targets = [p for p in token_data["pages"] if p["id"] == specific_target_id]
                else:
                    targets = [p for p in token_data["pages"] if p.get("selected")]
                
                # If nothing selected, use first available
                if not targets and token_data["pages"]:
                    targets = [token_data["pages"][0]]
            
            elif "accounts" in token_data:
                # Instagram support
                if specific_target_id:
                    targets = [a for a in token_data["accounts"] if a["id"] == specific_target_id]
                else:
                    targets = [a for a in token_data["accounts"] if a.get("selected")]
                
                if not targets and token_data["accounts"]:
                    targets = [token_data["accounts"][0]]
            
            if not targets:
                # Single-target default (TikTok, YouTube)
                targets = [{"id": "me", "name": "Default Profile", "type": "profile"}]
                
            # 2. Post to each target
            for target in targets:
                try:
                    target_name = target.get("name", "Unknown")
                    print(f"[POSTING] Publishing to {platform} -> {target_name} ({target['id']})")
                    
                    # ACTUAL POSTING LOGIC HERE (Simulated)
                    # ACTUAL POSTING LOGIC HERE (REAL API CALLS)
                    
                    # Resolve media path locally
                    local_media_path = None
                    if media_url:
                        # Extract filename
                        fname = os.path.basename(media_url)
                        
                        # Search directories for this file
                        search_dirs = [
                            '/app/generated_media/temp',
                            '/app/generated_media/temp/images',
                            '/app/generated_media/temp/videos',
                            '/app/generated_media/permanent/images',
                            '/app/generated_media/permanent/videos',
                            '/app/assets'
                        ]
                        
                        for d in search_dirs:
                            p = os.path.join(d, fname)
                            if os.path.exists(p):
                                local_media_path = p
                                break
                        
                        # Fallback: if media_url itself is a local path
                        if not local_media_path and os.path.exists(media_url):
                            local_media_path = media_url
                    
                    response = {}
                    
                    if platform == 'youtube':
                         if not local_media_path:
                             raise Exception("YouTube requires local file path, could not resolve from URL")
                         
                         # Check if it's an image (YouTube doesn't support images)
                         if local_media_path.endswith(('.png', '.jpg', '.jpeg')):
                             print(f"[SOCIAL PUBLISH] Skipping YouTube for image: {local_media_path}")
                             continue
                             
                         # Reconstruct credentials
                         creds_data = token_data
                         creds = google.oauth2.credentials.Credentials(
                                token=creds_data['access_token'],
                                refresh_token=creds_data.get('refresh_token'),
                                token_uri=creds_data.get('token_uri'),
                                client_id=creds_data.get('client_id'),
                                client_secret=creds_data.get('client_secret'),
                                scopes=creds_data.get('scopes')
                         )
                         
                         response = social_uploader.upload_video_youtube(
                             creds, 
                             post_data.get('title', 'New Video'), 
                             post_data.get('caption', ''), 
                             local_media_path
                         )
                         
                    elif platform == 'facebook':
                         # Use Page Token if available, otherwise User Token
                         fb_token = target.get('access_token', token_data['access_token'])
                         response = social_uploader.post_to_facebook(
                             fb_token,
                             target['id'],
                             post_data.get('caption'),
                             media_url,
                             title=post_data.get('title')
                         )
                         
                    elif platform == 'linkedin':
                         # Use Org/Member Token if available
                         li_token = target.get('access_token', token_data['access_token'])
                         response = social_uploader.post_to_linkedin(
                             li_token,
                             post_data.get('caption'),
                             media_url
                         )
                         
                    elif platform == 'instagram':
                         # Instagram uses the Page/Business access token from the linked Page
                         ig_token = target.get('access_token', token_data['access_token'])
                         
                         # Video Pre-processing for Reels (Must be 9:16)
                         final_media_url = media_url
                         if local_media_path and local_media_path.endswith(('.mp4', '.mov')):
                              try:
                                  print(f"[INSTAGRAM] Checking video format for {local_media_path}...")
                                  success, output_path = convert_to_9_16(local_media_path)
                                  if success:
                                      # Update URL to point to new resized video
                                      # We need to ensure the new file is accessible via URL
                                      # Assuming output_path is in /app/generated_media/...
                                      rel_path = output_path.replace('/app/generated_media/', '')
                                      final_media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
                                      print(f"[INSTAGRAM] Video resized/verified: {final_media_url}")
                                  else:
                                      print(f"[INSTAGRAM] Video resize failed: {output_path}")
                              except Exception as e:
                                  print(f"[INSTAGRAM] Video processing error: {e}")

                         response = social_uploader.post_to_instagram(
                             ig_token,
                             target['id'],
                             post_data.get('caption'),
                             final_media_url
                         )
                         
                    elif platform == 'tiktok':
                         # TikTok API Post (Real Implementation)
                         # Requires 'video.upload' scope
                         
                         # Check if video (TikTok only supports video)
                         if not media_path.endswith(('.mp4', '.mov')):
                             response = {"error": "TikTok only supports video files (.mp4, .mov)"}
                         else:
                             # Video Pre-processing for TikTok (Prefer 9:16)
                             final_local_path = local_media_path
                             try:
                                 print(f"[TIKTOK] Checking video format for {local_media_path}...")
                                 success, output_path = convert_to_9_16(local_media_path)
                                 if success:
                                     final_local_path = output_path
                                     print(f"[TIKTOK] Video resized/verified: {final_local_path}")
                             except Exception as e:
                                 print(f"[TIKTOK] Video processing error: {e}")

                             response = social_uploader.post_to_tiktok(
                                 token_data['access_token'],
                                 token_data['open_id'],
                                 final_local_path, # Must use local path for upload
                                 post_data.get('title', 'New TikTok')
                             )

                    else:
                         # Fallback
                         response = {"success": True, "url": f"https://{platform}.com"}
                    
                    # Process Response
                    if response.get("success"):
                        post_url = response.get("url", "https://vjgu.online")
                        add_log("Posting", "SUCCESS", f"Published to {platform}: {post_url}")
                        
                        if platform not in platforms_posted:
                            platforms_posted.append(platform)
                            results[platform] = post_url
                    else:
                        error_msg = response.get("error", "Unknown Error")
                        add_log("Posting", "ERROR", f"Failed to post to {platform}: {error_msg}")
                         
                except Exception as e:
                    add_log("Posting", "ERROR", f"Failed to post to {platform} ({target_name}): {str(e)}")

    except Exception as e:
        add_log("Posting", "ERROR", f"Global Posting Error: {e}")

    # Store in history
    published_history.insert(0, {
        "title": post_data.get('title'),
        "platforms": platforms_posted or target_platforms,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Published" if platforms_posted else "Failed"
    })
    
    return results




# -------------------------------------------------------------------
# Bulk Queue Logic & APIs
# -------------------------------------------------------------------

def process_queue():
    """Check queue for pending items and process them"""
    global schedule_queue
    
    # Simple lock to prevent concurrent processing if called frequently
    # For now, single threaded loop is fine
    
    now = datetime.datetime.now()
    modified = False
    
    for item in schedule_queue:
        if item['status'] == 'pending':
            try:
                scheduled_time = datetime.datetime.strptime(item['scheduled_time'], "%Y-%m-%dT%H:%M")
            except ValueError:
                # Try fallback format if seconds included
                 try:
                    scheduled_time = datetime.datetime.strptime(item['scheduled_time'], "%Y-%m-%d %H:%M:%S")
                 except:
                    print(f"[QUEUE] Invalid date format for {item['id']}")
                    item['status'] = 'failed'
                    modified = True
                    continue

            if now >= scheduled_time:
                print(f"[QUEUE] Processing item {item['id']}...")
                item['status'] = 'processing'
                save_schedule_queue() # Save state
                
                # Process each platform
                platforms = item.get('platforms', {})
                results = {}
                any_success = False
                
                # --- Facebook ---
                if platforms.get('facebook', {}).get('enabled'):
                    try:
                        fb_conf = platforms['facebook']
                        # Find token for page
                        fb_token = None
                        page_id = fb_conf.get('page_id')
                        
                        # Look up token in SOCIAL_TOKENS
                        if 'facebook' in SOCIAL_TOKENS:
                            for p in SOCIAL_TOKENS['facebook'].get('pages', []):
                                if p['id'] == page_id:
                                    fb_token = p['access_token']
                                    break
                                    
                        if fb_token:
                             # Resolve Media URL
                             # Ensure item['media_path'] is absolute local path
                             media_path = item['media_path']
                             rel_path = os.path.relpath(media_path, '/app/generated_media')
                             media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
                             
                             resp = social_uploader.post_to_facebook(fb_token, page_id, fb_conf.get('caption', ''), media_url, title=fb_conf.get('title'))
                             results['facebook'] = resp
                             if resp.get('success'): any_success = True
                        else:
                            results['facebook'] = {'error': 'Page token not found'}
                    except Exception as e:
                        results['facebook'] = {'error': str(e)}

                # --- LinkedIn ---
                if platforms.get('linkedin', {}).get('enabled'):
                    try:
                        li_conf = platforms['linkedin']
                        if 'linkedin' in SOCIAL_TOKENS:
                            token = SOCIAL_TOKENS['linkedin']['access_token']
                            media_path = item['media_path']
                            rel_path = os.path.relpath(media_path, '/app/generated_media')
                            media_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
                            
                            resp = social_uploader.post_to_linkedin(token, li_conf.get('caption', ''), media_url)
                            results['linkedin'] = resp
                            if resp.get('success') or resp.get('warning'): any_success = True
                        else:
                            results['linkedin'] = {'error': 'Not connected'}
                    except Exception as e:
                        results['linkedin'] = {'error': str(e)}

                # --- YouTube ---
                if platforms.get('youtube', {}).get('enabled'):
                    try:
                        yt_conf = platforms['youtube']
                        if 'youtube' in SOCIAL_TOKENS:
                            creds_data = SOCIAL_TOKENS['youtube']
                            creds = google.oauth2.credentials.Credentials(
                                token=creds_data['access_token'],
                                refresh_token=creds_data.get('refresh_token'),
                                token_uri=creds_data.get('token_uri'),
                                client_id=creds_data.get('client_id'),
                                client_secret=creds_data.get('client_secret'),
                                scopes=creds_data.get('scopes')
                            )
                            resp = social_uploader.upload_video_youtube(
                                creds, 
                                yt_conf.get('title', 'New Video'), 
                                yt_conf.get('description', ''), 
                                item['media_path']
                            )
                            results['youtube'] = resp
                            if resp.get('success'): any_success = True
                        else:
                            results['youtube'] = {'error': 'Not connected'}
                    except Exception as e:
                        results['youtube'] = {'error': str(e)}

                # --- Instagram ---
                if platforms.get('instagram', {}).get('enabled'):
                    try:
                        ig_conf = platforms['instagram']
                        # Instagram needs 9:16 video
                        # Check/Convert first
                        original_path = item['media_path']
                        final_url = None
                        
                        if original_path.endswith(('.mp4', '.mov')):
                            success, out_path = convert_to_9_16(original_path)
                            if success:
                                rel_path = os.path.relpath(out_path, '/app/generated_media')
                                final_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/{rel_path}"
                            else:
                                results['instagram'] = {'error': 'Video resize failed'}
                        
                        if final_url and 'facebook' in SOCIAL_TOKENS:
                            # Need page token + IG Business ID
                            # We'll try to find the linked page from the FB config
                            # This assumes the user selected a page that has IG linked
                            # For simplicity, we use the first page with IG linked or check specific ID if stored
                            
                            # Retrieve target page ID if stored, else search
                            target_page_id = ig_conf.get('page_id') # If we stored it
                            
                            found_page = None
                            ig_id = None
                            
                            for p in SOCIAL_TOKENS['facebook'].get('pages', []):
                                if p.get('instagram_business_account'):
                                    found_page = p
                                    ig_id = p['instagram_business_account']['id']
                                    break
                            
                            if found_page and ig_id:
                                resp = social_uploader.post_to_instagram(
                                    found_page['access_token'], 
                                    ig_id, 
                                    ig_conf.get('caption', ''), 
                                    final_url
                                )
                                results['instagram'] = resp
                                if resp.get('success'): any_success = True
                            else:
                                results['instagram'] = {'error': 'No linked IG account found'}
                        else:
                             if not final_url: pass # Already handled
                             else: results['instagram'] = {'error': 'Facebook/IG not connected'}

                    except Exception as e:
                        results['instagram'] = {'error': str(e)}

                # --- TikTok ---
                if platforms.get('tiktok', {}).get('enabled'):
                    try:
                         tk_conf = platforms['tiktok']
                         if 'tiktok' in SOCIAL_TOKENS:
                             # Resize to 9:16
                             original_path = item['media_path']
                             success, out_path = convert_to_9_16(original_path)
                             
                             if success:
                                 resp = social_uploader.post_to_tiktok(
                                     SOCIAL_TOKENS['tiktok']['access_token'],
                                     SOCIAL_TOKENS['tiktok'].get('open_id', 'me'),
                                     out_path,
                                     tk_conf.get('title', 'New TikTok')
                                 )
                                 results['tiktok'] = resp
                                 if resp.get('success'): any_success = True
                             else:
                                 results['tiktok'] = {'error': 'Video resize failed'}
                         else:
                             results['tiktok'] = {'error': 'Not connected'}
                    except Exception as e:
                        results['tiktok'] = {'error': str(e)}

                # Update Status
                item['results'] = results
                if any_success:
                    item['status'] = 'completed'
                else:
                    item['status'] = 'failed'  # Or partial_failed?
                
                item['processed_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                modified = True
                
    if modified:
        save_schedule_queue()

@app.route('/api/bulk-queue/add', methods=['POST'])
@login_required
def add_to_bulk_queue():
    try:
        data = request.json
        # Expecting: media_path, scheduled_time, platforms dict
        
        new_item = {
            "id": str(uuid.uuid4()),
            "media_path": data.get('media_path'), # Absolute path
            "scheduled_time": data.get('scheduled_time'), # ISO string YYYY-MM-DDTHH:MM
            "status": "pending",
            "platforms": data.get('platforms', {}),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        schedule_queue.append(new_item)
        save_schedule_queue()
        
        add_log("Queue", "INFO", f"Added content to queue for {new_item['scheduled_time']}")
        return jsonify({"success": True, "id": new_item['id']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/bulk-queue', methods=['GET'])
@login_required
def get_bulk_queue():
    # Sort by scheduled time?
    # For now just return list
    return jsonify(schedule_queue)

@app.route('/api/bulk-queue/<item_id>', methods=['DELETE'])
@login_required
def delete_bulk_queue_item(item_id):
    global schedule_queue
    original_len = len(schedule_queue)
    schedule_queue = [item for item in schedule_queue if item['id'] != item_id]
    
    if len(schedule_queue) < original_len:
        save_schedule_queue()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Item not found"})


def automation_loop():
    """
    Background worker for processing the Bulk Queue.
    """
    time.sleep(15)
    while True:
        # Check Bulk Queue
        try:
            process_queue()
        except Exception as e:
            add_log("Queue", "ERROR", f"Queue Check Failed: {e}")
            
        time.sleep(30)  # Check every 30 seconds


@app.route('/api/samples/upload', methods=['POST'])
@login_required
def upload_samples():
    """Bulk upload sample media files"""
    if 'files' not in request.files:
        return jsonify({"success": False, "error": "No files provided"}), 400
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    if not files or files[0].filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    os.makedirs(SAMPLES_DIR, exist_ok=True) # Ensure directory exists

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to prevent overwrites
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{int(time.time())}{ext}"
            
            save_path = os.path.join(SAMPLES_DIR, filename)
            file.save(save_path)
            
            uploaded_files.append({
                "filename": filename,
                "url": f"https://vjgu.online/assets/samples/{filename}",
                "type": "video" if ext.lower() in ['.mp4', '.mov', '.avi'] else "image" if ext.lower() in ['.png', '.jpg', '.jpeg'] else "audio"
            })
    
    return jsonify({
        "success": True,
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    })

@app.route('/api/samples', methods=['GET'])
@login_required
def list_samples():
    """List all uploaded sample media"""
    try:
        files = []
        if os.path.exists(SAMPLES_DIR):
            for f in sorted(os.listdir(SAMPLES_DIR), reverse=True):
                if allowed_file(f):
                    path = os.path.join(SAMPLES_DIR, f)
                    stats = os.stat(path)
                    ext = os.path.splitext(f)[1].lower()
                    
                    file_type = "unknown"
                    if ext in ['.mp4', '.mov', '.avi']: file_type = "video"
                    elif ext in ['.png', '.jpg', '.jpeg']: file_type = "image"
                    elif ext in ['.mp3', '.wav']: file_type = "audio"
                    
                    files.append({
                        "filename": f,
                        "url": f"https://vjgu.online/assets/samples/{f}",
                        "size_mb": round(stats.st_size / (1024 * 1024), 2),
                        "created": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_ctime)),
                        "type": file_type
                    })
        
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    add_log("System", "INFO", "Started")
    threading.Thread(target=automation_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
