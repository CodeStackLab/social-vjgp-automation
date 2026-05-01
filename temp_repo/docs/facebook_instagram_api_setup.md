# Facebook/Instagram API Setup Guide

Complete step-by-step guide to create a Meta (Facebook/Instagram) app and get API credentials for social media automation.

---

## Prerequisites

✅ Facebook Business Account
✅ Instagram Business/Creator Account (connected to Facebook Page)
✅ Facebook Page (required for Instagram API access)
✅ Valid email and phone number

---

## Step 1: Create Meta Developer Account

### 1.1 Register as Developer
1. Go to **https://developers.facebook.com/**
2. Click **"Get Started"** (top-right)
3. Log in with your Facebook account
4. Accept **Meta Platform Terms** and **Developer Policies**
5. Verify your account (email/phone if required)

### 1.2 Complete Developer Profile
- Add your **business details**
- Verify your **email address**
- Add **phone number** (for 2FA)

---

## Step 2: Create a New App

### 2.1 Create App
1. Go to **https://developers.facebook.com/apps/**
2. Click **"Create App"**
3. Select **"Business"** as app type
4. Click **"Next"**

### 2.2 App Details
Fill in the following:
- **App Name**: `VirtualJobGuru Social Automation` (or your choice)
- **App Contact Email**: `info@virtualjobguru.com`
- **Business Account**: Select your business account (or create one)
- Click **"Create App"**

### 2.3 Complete Security Check
- Solve the CAPTCHA
- Wait for app creation

---

## Step 3: Configure App Settings

### 3.1 Basic Settings
1. Go to **Settings** → **Basic** (left sidebar)
2. Note down:
   - **App ID**: `123456789012345` (example)
   - **App Secret**: Click **"Show"** → Copy the secret key

> ⚠️ **IMPORTANT**: Never share your App Secret publicly!

### 3.2 Add App Domain
1. Scroll to **"App Domains"**
2. Add: `vjgu.online`
3. Click **"Save Changes"**

### 3.3 Privacy Policy & Terms
1. Add **Privacy Policy URL**: `https://vjgu.online/privacy`
2. Add **Terms of Service URL**: `https://vjgu.online/terms`
3. Click **"Save Changes"**

---

## Step 4: Add Instagram Product

### 4.1 Add Instagram Basic Display
1. Go to **Dashboard** (left sidebar)
2. Scroll to **"Add Products"**
3. Find **"Instagram Basic Display"**
4. Click **"Set Up"**

### 4.2 Configure Instagram Settings
1. Go to **Instagram Basic Display** → **Basic Display**
2. Click **"Create New App"**
3. Fill in:
   - **Display Name**: `VirtualJobGuru`
   - **Valid OAuth Redirect URIs**: 
     ```
     https://vjgu.online/auth/instagram/callback
     ```
   - **Deauthorize Callback URL**: 
     ```
     https://vjgu.online/auth/instagram/deauthorize
     ```
   - **Data Deletion Request URL**: 
     ```
     https://vjgu.online/auth/instagram/delete
     ```
4. Click **"Save Changes"**

### 4.3 Get Instagram Credentials
1. Note down:
   - **Instagram App ID**: `987654321098765` (example)
   - **Instagram App Secret**: Click **"Show"** → Copy
   - **Client Token**: Copy this as well

---

## Step 5: Add Facebook Login Product

### 5.1 Add Facebook Login
1. Go to **Dashboard**
2. Find **"Facebook Login"**
3. Click **"Set Up"**
4. Select **"Web"** platform

### 5.2 Configure OAuth Settings
1. Go to **Facebook Login** → **Settings**
2. Add **Valid OAuth Redirect URIs**:
   ```
   https://vjgu.online/auth/facebook/callback
   ```
3. Enable **"Client OAuth Login"**: ON
4. Enable **"Web OAuth Login"**: ON
5. Click **"Save Changes"**

---

## Step 6: Request Permissions

### 6.1 Instagram Permissions
Go to **App Review** → **Permissions and Features**

Request the following permissions:
- ✅ `instagram_basic` - Basic profile access
- ✅ `instagram_content_publish` - Publish posts
- ✅ `pages_show_list` - List pages
- ✅ `pages_read_engagement` - Read engagement

### 6.2 Facebook Permissions
Request:
- ✅ `pages_manage_posts` - Manage page posts
- ✅ `pages_read_engagement` - Read page engagement
- ✅ `publish_video` - Publish videos

### 6.3 Submit for Review
1. Click **"Request"** for each permission
2. Provide **use case description**:
   ```
   This app automates social media posting for VirtualJobGuru, 
   a career coaching platform. We need to publish educational 
   content (videos and images) about job interviews, resume tips, 
   and career advice to our Instagram and Facebook pages.
   ```
3. Upload **demo video** showing your app functionality
4. Click **"Submit for Review"**

> ⏳ Review takes 3-7 business days

---

## Step 7: Get Access Tokens

### 7.1 Generate User Access Token (Testing)
1. Go to **Tools** → **Graph API Explorer**
2. Select your app from dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
5. Click **"Generate Access Token"**
6. Copy the token

### 7.2 Get Long-Lived Token
1. Go to **Access Token Debugger**: https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your token
3. Click **"Debug"**
4. Click **"Extend Access Token"**
5. Copy the **long-lived token** (valid for 60 days)

### 7.3 Get Page Access Token
1. Go to **Graph API Explorer**
2. Use this query:
   ```
   GET /me/accounts
   ```
3. Click **"Submit"**
4. Find your page in response
5. Copy the **access_token** for your page

### 7.4 Get Instagram Business Account ID
1. Use this query (replace `PAGE_ID` with your page ID):
   ```
   GET /PAGE_ID?fields=instagram_business_account
   ```
2. Copy the **instagram_business_account** → **id**

---

## Step 8: Configure in Your App

### 8.1 Update Settings File
Add to your `app_settings.json`:

```json
{
  "social_config": {
    "facebook": {
      "app_id": "YOUR_FACEBOOK_APP_ID",
      "app_secret": "YOUR_FACEBOOK_APP_SECRET",
      "page_id": "YOUR_PAGE_ID",
      "page_access_token": "YOUR_PAGE_ACCESS_TOKEN"
    },
    "instagram": {
      "app_id": "YOUR_INSTAGRAM_APP_ID",
      "app_secret": "YOUR_INSTAGRAM_APP_SECRET",
      "business_account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID",
      "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN"
    }
  }
}
```

### 8.2 Test Connection
1. Go to your app: `https://vjgu.online/`
2. Navigate to **Settings** tab
3. Click **"Connect Facebook"**
4. Authorize the app
5. Click **"Connect Instagram"**
6. Authorize the app

---

## Step 9: Go Live (Production)

### 9.1 Complete App Review
1. Ensure all permissions are **approved**
2. Add **Privacy Policy** and **Terms of Service**
3. Add **App Icon** (1024x1024px)
4. Complete **Data Use Checkup**

### 9.2 Switch to Live Mode
1. Go to **Settings** → **Basic**
2. Toggle **"App Mode"** from **Development** to **Live**
3. Confirm the switch

---

## Important URLs

| Resource | URL |
|----------|-----|
| Developer Dashboard | https://developers.facebook.com/apps/ |
| Graph API Explorer | https://developers.facebook.com/tools/explorer/ |
| Access Token Debugger | https://developers.facebook.com/tools/debug/accesstoken/ |
| App Review Status | https://developers.facebook.com/apps/YOUR_APP_ID/app-review/ |
| Instagram API Docs | https://developers.facebook.com/docs/instagram-api |
| Facebook Pages API | https://developers.facebook.com/docs/pages |

---

## Troubleshooting

### Issue: "Invalid OAuth Redirect URI"
**Solution**: Make sure redirect URI in app settings exactly matches your callback URL (including https://)

### Issue: "Permissions Not Approved"
**Solution**: Submit detailed use case with demo video. Be specific about how you'll use each permission.

### Issue: "Token Expired"
**Solution**: Generate new long-lived token or implement token refresh logic.

### Issue: "Instagram Account Not Found"
**Solution**: Ensure Instagram account is:
- Converted to **Business** or **Creator** account
- Connected to a **Facebook Page**
- Page is owned by the same Facebook account

---

## Security Best Practices

✅ **Never commit** API keys to Git (use `.env` files)
✅ **Rotate tokens** regularly (every 60 days)
✅ **Use HTTPS** for all callbacks
✅ **Implement rate limiting** to avoid API bans
✅ **Store tokens encrypted** in database
✅ **Monitor API usage** in Meta Business Suite

---

## Next Steps

1. ✅ Create Meta Developer Account
2. ✅ Create App and get credentials
3. ✅ Request permissions
4. ✅ Get access tokens
5. ✅ Configure in your application
6. ✅ Test posting functionality
7. ✅ Submit for app review
8. ✅ Go live!

---

## Support

- **Meta Developer Support**: https://developers.facebook.com/support/
- **Community Forum**: https://developers.facebook.com/community/
- **Instagram API Issues**: https://developers.facebook.com/support/bugs/

---

**Created**: 2026-02-04  
**Last Updated**: 2026-02-04  
**Version**: 1.0
