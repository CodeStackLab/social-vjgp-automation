
import os
import requests
import json
import time

def post_to_linkedin(token, text, media_url=None):
    """
    Post logic for LinkedIn using UGC API.
    Handles text and media URLs.
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        # 1. Get URN (Person) - Try v2/me first, then userinfo (OpenID)
        person_id = None
        me_resp = requests.get('https://api.linkedin.com/v2/me', headers=headers)
        if me_resp.status_code == 200:
            person_id = me_resp.json().get('id')
        else:
            # Try OpenID userinfo as fallback (common for new apps)
            ui_resp = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
            if ui_resp.status_code == 200:
                person_id = ui_resp.json().get('sub')
        
        if not person_id:
            return {"error": f"Failed to get LinkedIn profile ID. v2/me: {me_resp.text}, userinfo: {ui_resp.text if 'ui_resp' in locals() else 'N/A'}"}
            
        person_urn = f"urn:li:person:{person_id}"
        
        # Base post structure
        post_body = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # If media URL provided
        if media_url:
            post_body["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            post_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "description": {"text": text[:100]},
                    "originalUrl": media_url,
                    "title": {"text": "VirtualJobGuru Update"}
                }
            ]

        resp = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=post_body)
        
        if resp.status_code == 201:
            data = resp.json()
            urn = data.get('id')
            return {"success": True, "id": urn, "url": f"https://www.linkedin.com/feed/update/{urn}/"}
            
        # Handle Duplicate Post as Success/Warning
        if resp.status_code == 422 and "DUPLICATE_POST" in resp.text:
             return {"success": True, "warning": "Content already posted (Duplicate identified by LinkedIn)", "url": "https://www.linkedin.com/feed/"}
        
        return {"error": f"LinkedIn API Error: {resp.status_code} - {resp.text}"}

    except Exception as e:
        return {"error": str(e)}

def post_to_facebook(access_token, page_id, text, media_url=None, title=None):
    """
    Post to Facebook Page via Graph API.
    """
    try:
        base_url = f"https://graph.facebook.com/v19.0/{page_id}"
        payload = {'access_token': access_token}
        
        # Truncate text (caption/message) to safe limit
        safe_text = text[:2000] if text else ""
        
        if media_url:
            # Check if video
            is_video = media_url.endswith(('.mp4', '.mov', '.avi'))
            if is_video:
                endpoint = f"{base_url}/videos"
                payload['description'] = safe_text
                payload['file_url'] = media_url
                if title:
                    payload['title'] = title[:255]
                    print(f"[FACEBOOK] Final title being sent to API: {payload['title']} (Original length: {len(title)})")

            else:
                endpoint = f"{base_url}/photos"
                payload['message'] = safe_text
                payload['url'] = media_url
        else:
            endpoint = f"{base_url}/feed"
            payload['message'] = safe_text
            
        resp = requests.post(endpoint, data=payload)
        data = resp.json()
        
        if 'id' in data:
            post_id = data['id']
            return {"success": True, "id": post_id, "url": f"https://www.facebook.com/{post_id}"}
        
        return {"error": f"Facebook API Error: {data}"}
        
    except Exception as e:
        return {"error": str(e)}

def post_to_instagram(access_token, ig_user_id, text, media_url):
    """
    Post to Instagram Business Account via Graph API.
    Requires: instagram_content_publish scope.
    """
    try:
        if not media_url:
            return {"error": "Instagram requires media URL"}
            
        is_video = media_url.endswith(('.mp4', '.mov', '.avi'))
        media_type = "VIDEO" if is_video else "IMAGE"
        
        # Step 1: Create Container
        container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        payload = {
            'caption': text,
            'access_token': access_token
        }
        
        if is_video:
            payload['video_url'] = media_url
            payload['media_type'] = 'REELS' 
        else:
            payload['image_url'] = media_url
            
        resp = requests.post(container_url, data=payload)
        data = resp.json()
        
        if 'id' not in data:
            return {"error": f"IG Container Failed: {data}"}
            
        creation_id = data['id']
        
        # Wait for processing (with retries)
        if is_video:
            print(f"[INSTAGRAM] Waiting for video processing (creation_id: {creation_id})...")
            max_retries = 3
            for i in range(max_retries):
                time.sleep(20)  # Wait 20s per retry
                status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
                status_resp = requests.get(status_url, params={'access_token': access_token, 'fields': 'status_code,status'})
                status_data = status_resp.json()
                print(f"[INSTAGRAM] Status check {i+1}/{max_retries}: {status_data}")
                
                if status_data.get('status_code') == 'FINISHED':
                    break
                elif status_data.get('status_code') == 'ERROR':
                     error_msg = f"IG Processing Error: {status_data}"
                     # Check for aspect ratio error
                     if '2207076' in str(status_data) or 'aspect ratio' in str(status_data).lower():
                         error_msg = "Instagram Reels require 9:16 aspect ratio (1080x1920). Please use a vertical video."
                     return {"error": error_msg}
 
            
        # Step 2: Publish Container
        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        pub_payload = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        pub_resp = requests.post(publish_url, data=pub_payload)
        pub_data = pub_resp.json()
        
        if 'id' in pub_data:
            # We can try to fetch the permalink
            # GET /{ig-media-id}?fields=permalink
            try:
                perm_resp = requests.get(f"https://graph.facebook.com/v19.0/{pub_data['id']}?fields=permalink&access_token={access_token}")
                if perm_resp.status_code == 200:
                    permalink = perm_resp.json().get('permalink')
                    return {"success": True, "id": pub_data['id'], "url": permalink}
            except:
                pass
                
            return {"success": True, "id": pub_data['id'], "url": f"https://instagram.com"}
            
        return {"error": f"IG Publish Failed: {pub_data}"}

    except Exception as e:
        return {"error": str(e)}

def upload_video_youtube(credentials, title, description, file_path, category_id="22", privacy_status="public"):
    """
    Upload video to YouTube using Google API Client.
    credentials: valid google.oauth2.credentials.Credentials object
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        youtube = build("youtube", "v3", credentials=credentials)
        
        body = {
            "snippet": {
                "title": title[:100],
                "description": (description or "")[:5000],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }
        print(f"[YOUTUBE] Final title being sent to API: {body['snippet']['title']} (Original length: {len(title)})")

        
        # Split file path if it's a URL (assuming it's local for now as Upload requires local file or stream)
        # If media_url is http, we need to download it first. 
        # For this implementation, we assume file_path is LOCAL path from main.py
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[YOUTUBE] Uploading... {int(status.progress() * 100)}%")
                
        if 'id' in response:
            video_id = response['id']
            return {"success": True, "id": video_id, "url": f"https://youtu.be/{video_id}"}
            
        return {"error": f"YouTube Upload Failed: {response}"}


    except Exception as e:
        return {"error": str(e)}

def post_to_tiktok(access_token, open_id, video_path, title):
    """
    Post video to TikTok via Direct Post API (v2).
    Requires 'video.upload' scope.
    """
    try:
        if not os.path.exists(video_path):
             return {"error": f"TikTok: Video file not found at {video_path}"}
             
        file_size = os.path.getsize(video_path)
        
        # Step 1: Initialize Upload
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        # Determine privacy - defaulting to SELF_ONLY for safety during tests, user can change to PUBLIC_TO_EVERYONE
        # Actually let's use PUBLIC if it's a real post
        privacy = "PUBLIC_TO_EVERYONE"
        
        payload = {
            "post_info": {
                "title": title[:150], # Max 150 chars usually
                "privacy_level": privacy,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size, 
                "total_chunk_count": 1
            }
        }
        
        init_resp = requests.post(init_url, headers=headers, json=payload)
        init_data = init_resp.json()
        
        if 'data' not in init_data or 'upload_url' not in init_data['data']:
             return {"error": f"TikTok Init Failed: {init_data}"}
             
        upload_url = init_data['data']['upload_url']
        publish_id = init_data['data']['publish_id']
        
        # Step 2: Upload Video
        with open(video_path, 'rb') as f:
            video_data = f.read()
            
        upload_headers = {
            'Content-Type': 'video/mp4',
            'Content-Length': str(file_size),
            'Content-Range': f'bytes 0-{file_size-1}/{file_size}'
        }
        
        upload_resp = requests.put(upload_url, headers=upload_headers, data=video_data)
        
        if upload_resp.status_code not in [200, 201]:
             return {"error": f"TikTok Upload Failed: {upload_resp.status_code} - {upload_resp.text}"}
             
        # TikTok automatically finalizes after upload for this endpoint?
        # Usually yes for FILE_UPLOAD source.
        
        return {"success": True, "id": publish_id, "url": "https://www.tiktok.com/@me"} # URL is hard to guess immediately

    except Exception as e:
        return {"error": f"TikTok Exception: {str(e)}"}
