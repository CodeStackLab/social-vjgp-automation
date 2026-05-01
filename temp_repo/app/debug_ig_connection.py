
import json
import os
import requests
import sys

# Load settings
try:
    with open('/app/data/app_settings.json', 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    print("Settings file not found.")
    sys.exit(1)

tokens = settings.get('social_tokens', {})
fb_data = tokens.get('facebook', {})

if not fb_data:
    print("No Facebook token found.")
    sys.exit(1)

user_access_token = fb_data.get('access_token')
p_len = len(user_access_token) if user_access_token else 0
print(f"User Token Length: {p_len}")

# 1. Get all pages with extra fields
print("\nFetching Pages & Linked Accounts...")
url = "https://graph.facebook.com/v19.0/me/accounts"
params = {
    'access_token': user_access_token,
    'fields': 'name,id,access_token,instagram_business_account,connected_instagram_account'
}

try:
    resp = requests.get(url, params=params)
    data = resp.json()

    if 'error' in data:
        print(f"Error: {data}")
        sys.exit(1)

    pages = data.get('data', [])
    print(f"Found {len(pages)} pages.")

    found_ig = False
    for i, page in enumerate(pages):
        print(f"\n--- Page {i+1}: {page.get('name')} ({page.get('id')}) ---")
        
        # Check Business Account
        ig_bus = page.get('instagram_business_account')
        if ig_bus:
            found_ig = True
            print(f"✅ LINKED Instagram Business ID: {ig_bus.get('id')}")
            # Try to fetch IG details
            ig_url = f"https://graph.facebook.com/v19.0/{ig_bus.get('id')}"
            try:
                ig_resp = requests.get(ig_url, params={'fields': 'username,name,followers_count', 'access_token': page.get('access_token')})
                print(f"   Details: {ig_resp.json()}")
            except Exception as e:
                print(f"   Error fetching details: {e}")
        else:
            print("❌ No 'instagram_business_account' field returned.")
            
        # Check connected_instagram_account (older field, sometimes useful for non-business)
        ig_conn = page.get('connected_instagram_account')
        if ig_conn:
            print(f"ℹ️  'connected_instagram_account' present: {ig_conn} (This is usually not enough for API posting)")

    if not found_ig:
        print("\n[CONCLUSION] No Instagram Business Account found linked to any page.")
        print("Possible Reasons:")
        print("1. Account is Personal/Creator, not Business.")
        print("2. Link is missing in Facebook Page settings.")
        print("3. 'instagram_basic' or 'pages_show_list' permission missing (Unlikely if pages are shown).")

except Exception as e:
    print(f"Request failed: {e}")

print("\nDebug Complete.")
