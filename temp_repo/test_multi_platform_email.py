#!/usr/bin/env python3
"""
Test script to send SEPARATE approval emails for each platform
"""
import os
import sys
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Load SMTP settings
CONFIG_FILE = "/app/data/app_settings.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        settings = json.load(f)
        smtp_settings = settings.get('smtp_settings', {})
else:
    print("❌ app_settings.json not found!")
    sys.exit(1)

if not smtp_settings.get('enabled', False):
    print("❌ SMTP is not enabled!")
    sys.exit(1)

# Platform-specific character limits
PLATFORM_LIMITS = {
    "Facebook": {"title": 100, "caption": 63206},
    "Instagram": {"title": 100, "caption": 2200},
    "LinkedIn": {"title": 100, "caption": 3000},
    "TikTok": {"title": 100, "caption": 2200}
}

def truncate_text(text, limit):
    """Truncate text to fit platform limit"""
    if len(text) <= limit:
        return text
    return text[:limit-3] + "..."

def send_platform_email(platform, post_data, video_path=None, image_path=None):
    """Send approval email for specific platform"""
    
    # Apply platform-specific limits
    limits = PLATFORM_LIMITS.get(platform, {"title": 100, "caption": 2200})
    title = truncate_text(post_data['title'], limits['title'])
    caption = truncate_text(post_data['caption'], limits['caption'])
    
    approval_id = f"{platform.lower()}_{int(time.time() * 1000)}"
    domain = "vjgu.online"
    approve_url = f"https://{domain}/api/approve-post/{approval_id}"
    decline_url = f"https://{domain}/api/decline-post/{approval_id}"
    
    # Platform emoji
    platform_emoji = {
        "Facebook": "📘",
        "Instagram": "📸",
        "LinkedIn": "💼",
        "TikTok": "🎵"
    }
    emoji = platform_emoji.get(platform, "📱")
    
    # Create email
    msg = MIMEMultipart('mixed')
    msg['From'] = smtp_settings.get("sender_email")
    msg['To'] = smtp_settings.get("recipient_email")
    msg['Subject'] = f"{emoji} {platform} Approval: {title}"
    
    # Extract hashtags
    hashtags = ' '.join([word for word in caption.split() if word.startswith('#')])
    
    # HTML body
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .platform-badge {{ display: inline-block; padding: 8px 16px; background: #6366f1; color: white; border-radius: 20px; font-weight: bold; margin-bottom: 20px; }}
            h2 {{ color: #333; margin-top: 0; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #6366f1; border-radius: 5px; }}
            .label {{ font-weight: bold; color: #555; }}
            .content {{ margin-top: 5px; color: #333; white-space: pre-wrap; }}
            .limit-info {{ font-size: 12px; color: #888; margin-top: 5px; }}
            .buttons {{ margin-top: 30px; text-align: center; }}
            .btn {{ display: inline-block; padding: 15px 40px; margin: 10px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; }}
            .btn-approve {{ background: #10b981; color: white; }}
            .btn-decline {{ background: #ef4444; color: white; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #888; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="platform-badge">{emoji} {platform}</div>
            <h2>Post Approval Required</h2>
            
            <div class="section">
                <div class="label">📌 Title:</div>
                <div class="content">{title}</div>
                <div class="limit-info">Character limit: {len(title)}/{limits['title']}</div>
            </div>
            
            <div class="section">
                <div class="label">📝 Caption:</div>
                <div class="content">{caption}</div>
                <div class="limit-info">Character limit: {len(caption)}/{limits['caption']}</div>
            </div>
            
            <div class="section">
                <div class="label">🏷️ Hashtags:</div>
                <div class="content">{hashtags or 'None'}</div>
            </div>
            
            <div class="section">
                <div class="label">📱 Platform:</div>
                <div class="content">{platform}</div>
            </div>
            
            <div class="section">
                <div class="label">📹 Media Type:</div>
                <div class="content">{post_data['type']}</div>
            </div>
            
            <div class="section">
                <div class="label">📎 Attachment:</div>
                <div class="content">{'Video' if video_path else 'Image'} file attached</div>
            </div>
            
            <div class="section">
                <div class="label">👤 Client Info:</div>
                <div class="content">
                    <strong>Brand:</strong> VirtualJobGuru<br>
                    <strong>Contact:</strong> +49 1577 4331858<br>
                    <strong>Email:</strong> info@virtualjobguru.com<br>
                    <strong>Website:</strong> www.virtualjobguru.com
                </div>
            </div>
            
            <div class="buttons">
                <a href="{approve_url}" class="btn btn-approve">✅ APPROVE & POST TO {platform.upper()}</a>
                <a href="{decline_url}" class="btn btn-decline">❌ DECLINE</a>
            </div>
            
            <div class="footer">
                <p>VirtualJobGuru Social Automation System</p>
                <p>This post will be published to <strong>{platform}</strong> only after approval.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach media file
    media_file = video_path or image_path
    if media_file and os.path.exists(media_file):
        try:
            with open(media_file, 'rb') as f:
                media_data = f.read()
            
            media_type = 'video/mp4' if video_path else 'image/png'
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(media_data)
            encoders.encode_base64(attachment)
            
            filename = f"{platform.lower()}_{'video' if video_path else 'image'}.{'mp4' if video_path else 'png'}"
            attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(attachment)
            
            print(f"  ✅ Attached: {os.path.basename(media_file)} ({len(media_data) / 1024 / 1024:.2f} MB)")
        except Exception as e:
            print(f"  ❌ Failed to attach media: {e}")
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_settings['smtp_server'], int(smtp_settings['smtp_port']))
        server.starttls()
        server.login(smtp_settings['sender_email'], smtp_settings['app_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"  ✅ Email sent for {platform}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to send {platform} email: {e}")
        return False

# Test data
post_data = {
    "title": "Top 5 Interview Tips for 2026 - Land Your Dream Job!",
    "caption": """Master these essential interview techniques to stand out from the competition! 

🎯 Key Takeaways:
1. Research the company thoroughly
2. Practice STAR method responses
3. Prepare thoughtful questions
4. Dress professionally
5. Follow up within 24 hours

#InterviewTips #CareerAdvice #JobSearch #ProfessionalDevelopment #CareerGrowth #JobInterview #HRTips #CareerSuccess #JobHunting #InterviewPrep""",
    "type": "Video Reel",
    "created_at": "2026-02-04 20:35:00"
}

# Video file
VIDEO_PATH = "/app/generated_media/videos/branded_reel_1770052913.mp4"

# Platforms to test
platforms = ["Facebook", "Instagram", "LinkedIn", "TikTok"]

print("\n🚀 Sending SEPARATE approval emails for each platform...\n")

success_count = 0
for platform in platforms:
    print(f"\n📧 {platform}:")
    if send_platform_email(platform, post_data, video_path=VIDEO_PATH):
        success_count += 1
    time.sleep(1)  # Small delay between emails

print(f"\n\n✅ Successfully sent {success_count}/{len(platforms)} emails!")
print(f"\n📬 Check your inbox: {smtp_settings['recipient_email']}")
