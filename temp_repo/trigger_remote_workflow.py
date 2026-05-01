import requests
import json
import time

# Configuration
BASE_URL = "https://vjgu.online"
USERNAME = "admin"
PASSWORD = "VJGU_Secure_Research_2026!@#"

def main():
    session = requests.Session()
    
    # 1. Login
    print(f"🔐 Logging in to {BASE_URL}...")
    login_payload = {
        "username": USERNAME, 
        "password": PASSWORD
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_payload)
        if response.status_code == 200 and "Dashboard" in response.text:
            print("✅ Login successful")
        else:
            # Check if already logged in or handle redirects
            if response.status_code == 200:
                 print("✅ Login successful (200 OK)")
            else:
                print(f"❌ Login failed: {response.status_code}")
                # print(response.text)
                return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Enable SMTP (Email Approval)
    print("\n📧 Enabling Email Approval Workflow...")
    smtp_settings = {
        "enabled": True
    }
    
    response = session.post(f"{BASE_URL}/api/settings/smtp", json=smtp_settings)
    if response.status_code == 200:
        print("✅ SMTP enabled successfully")
    else:
        print(f"❌ Failed to enable SMTP: {response.text}")
        return

    # 3. Queue a new Post
    print("\n📝 Queueing new 'Special Career Guide' IMAGE post...")
    new_posts = {
        "posts": [
            {
                "title": "Special Career Guide - Image Post",
                "caption": "Here is the special career guide you requested. #CareerSuccess #VisualGuide #HR",
                "type": "post", # Triggers image generation
                "visual_prompt": "modern minimalist office desk with a laptop and a plant, high quality professional photography, bright and airy",
                "logo": "Default"
            }
        ]
    }
    
    response = session.post(f"{BASE_URL}/api/bulk-create", json=new_posts)
    if response.status_code == 200:
        print("✅ Post queued successfully")
    else:
        print(f"❌ Failed to queue post: {response.text}")
        return

    # 4. Trigger Generation/Processing
    print("\n🚀 Triggering content generation...")
    # The /api/test/trigger endpoint processes the first item in the planner queue
    response = session.post(f"{BASE_URL}/api/test/trigger", json={})
    
    if response.status_code == 200:
        print("✅ Generation triggered successfully!")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # AUTOMATICALLY APPROVE FOR VERIFICATION - DISABLED FOR USER TESTING
            # if "results" in data:
            #     print("\n🕵️ Verifying Approval Workflow...")
            #     for item in data["results"]:
            #         approval_id = item.get("approval_id")
            #         platform = item.get("platform")
            #         
            #         if approval_id:
            #             print(f"👉 Approving {platform} post ({approval_id})...")
            #             # approve_resp = session.get(f"{BASE_URL}/api/approve-post/{approval_id}")
            #             
            #             # if approve_resp.status_code == 200 and "Approved & Published" in approve_resp.text:
            #             #     print(f"✅ {platform} Approved Successfully!")
            #             # else:
            #             #     print(f"❌ {platform} Approval Failed: {approve_resp.status_code}")
            #             #     # print(approve_resp.text[:200])
            #             print(f"⚠️ Auto-approval skipped. Please approve manually via email: {item.get('approval_id')}")
        except Exception as e:
             print(f"❌ Error parsing response or approving: {e}")
             print(response.text)
    else:
        print(f"❌ Failed to trigger generation: {response.text}")

    print("\n✅ WORKFLOW COMPLETE")
    print("Please check your email. After clicking APPROVE, you should see the live social media links on the confirmation page.")

if __name__ == "__main__":
    main()
