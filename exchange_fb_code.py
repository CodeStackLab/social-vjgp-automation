import json
import urllib.request
import urllib.parse
import ssl

APP_ID = "1901738023959051"
APP_SECRET = "916d8723044900700580a7fcbede5d0a"
REDIRECT_URI = "https://vjgu.online/auth-callback"
CODE = "AQDNAne1UqZRPZI_Edt1ceUVW9HAPVEGE8NDu3SBVq_sLawKSZZCc-LN0S6DLeU-OmklfgNAprapyIUYA-mGGonLizwad9dbq8UuaCG_5rgnJeR6eJmvGkAqRU65r8u6dK1ntuII5StN-dQuJPwNg1Qv6lg1LQ5J7DObB1zx2ElIox3hfW4LRZFcvYZCDYgxVLcw2St7cTIg_n4LQ5DIIKC8-etx-pCe8LEZS05v0BbfzQjYaBFz1J4BI6ims3d5QDiczGd-Exsjzjx6QlXGx0B5SPJ4hYZbOEJc4STti_Q9y3B0tHu8Aih4fTE4OWgsf8vHX2NOsxk9N8GFX391yc1MGbTGT_W62y7rXRU-TecvnCubWbHNnoDXNdCKXtNMAMxjAziPD6xM061Z84yxZr7XnsRx0M5-VRxPQwXLfbvI42yA-mFmaHHtwZX2aLRm55PvT2f0QIMqd62WMTMkCHCd"

def get_json(url):
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as response:
        return json.loads(response.read().decode())

def exchange_token():
    try:
        # 1. Exchange Code for Short-Lived User Access Token
        print("Exchanging code for token...")
        params = urllib.parse.urlencode({
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": CODE
        })
        url = f"https://graph.facebook.com/v19.0/oauth/access_token?{params}"
        token_data = get_json(url)
        short_token = token_data.get("access_token")

        # 2. Exchange for Long-Lived User Access Token
        print("Exchanging for long-lived token...")
        params = urllib.parse.urlencode({
            "grant_type": "fb_exchange_token",
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "fb_exchange_token": short_token
        })
        url = f"https://graph.facebook.com/v19.0/oauth/access_token?{params}"
        long_token_data = get_json(url)
        long_token = long_token_data.get("access_token")

        # 3. Get Instagram/Page IDs
        print("Fetching account details...")
        params = urllib.parse.urlencode({
            "fields": "instagram_business_account,name,access_token",
            "access_token": long_token
        })
        url = f"https://graph.facebook.com/v19.0/me/accounts?{params}"
        accounts_data = get_json(url)
        
        print("\n--- RESULTS ---")
        for account in accounts_data.get("data", []):
            name = account.get("name")
            page_id = account.get("id")
            page_token = account.get("access_token")
            insta_account = account.get("instagram_business_account")
            print(f"Page Name: {name}")
            print(f"Page ID: {page_id}")
            print(f"Page Access Token: {page_token}")
            if insta_account:
                print(f"Instagram Business ID: {insta_account.get('id')}")
            print("----------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    exchange_token()
