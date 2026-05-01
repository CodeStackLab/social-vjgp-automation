#!/usr/bin/env python3
"""
Test script to send approval email with video attachment
"""
import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Load SMTP settings from app_settings.json
CONFIG_FILE = "/app/data/app_settings.json"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        settings = json.load(f)
        smtp_settings = settings.get('smtp_settings', {})
else:
    print("❌ app_settings.json not found!")
    sys.exit(1)

# Check if SMTP is enabled
if not smtp_settings.get('enabled', False):
    print("❌ SMTP is not enabled in settings!")
    sys.exit(1)

# Video file path
VIDEO_PATH = "/app/generated_media/videos/branded_reel_1770052913.mp4"

if not os.path.exists(VIDEO_PATH):
    print(f"❌ Video not found: {VIDEO_PATH}")
    sys.exit(1)

# Test post data
post_data = {
    "title": "Test Video Post - Approval Required",
    "caption": "This is a test video post for approval workflow. #TestPost #Automation #VideoContent",
    "platforms": ["Instagram", "Facebook", "LinkedIn"],
    "type": "Video Reel",
    "created_at": "2026-02-04 20:30:00",
    "video_path": VIDEO_PATH
}

approval_id = "test_123"
domain = "vjgu.online"
approve_url = f"https://{domain}/api/approve-post/{approval_id}"
decline_url = f"https://{domain}/api/decline-post/{approval_id}"

# Create email
msg = MIMEMultipart('mixed')
msg['From'] = smtp_settings.get("sender_email")
msg['To'] = smtp_settings.get("recipient_email")
msg['Subject'] = f"📋 Approval Required: {post_data['title']}"

# Email body
caption_text = post_data.get('caption', 'N/A')
hashtags = ' '.join([word for word in caption_text.split() if word.startswith('#')])

html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h2 {{ color: #333; margin-top: 0; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #6366f1; border-radius: 5px; }}
        .label {{ font-weight: bold; color: #555; }}
        .content {{ margin-top: 5px; color: #333; white-space: pre-wrap; }}
        .buttons {{ margin-top: 30px; text-align: center; }}
        .btn {{ display: inline-block; padding: 15px 40px; margin: 10px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; }}
        .btn-approve {{ background: #10b981; color: white; }}
        .btn-decline {{ background: #ef4444; color: white; }}
        .btn:hover {{ opacity: 0.9; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 NEW SOCIAL MEDIA POST READY FOR APPROVAL</h2>
        
        <div class="section">
            <div class="label">📌 Title:</div>
            <div class="content">{post_data['title']}</div>
        </div>
        
        <div class="section">
            <div class="label">📝 Caption:</div>
            <div class="content">{caption_text}</div>
        </div>
        
        <div class="section">
            <div class="label">🏷️ Hashtags:</div>
            <div class="content">{hashtags or 'None'}</div>
        </div>
        
        <div class="section">
            <div class="label">📱 Platforms:</div>
            <div class="content">{', '.join(post_data['platforms'])}</div>
        </div>
        
        <div class="section">
            <div class="label">📹 Type:</div>
            <div class="content">{post_data['type']}</div>
        </div>
        
        <div class="section">
            <div class="label">📎 Attachment:</div>
            <div class="content">Video file attached (see below)</div>
        </div>
        
        <div class="buttons">
            <a href="{approve_url}" class="btn btn-approve">✅ APPROVE & POST</a>
            <a href="{decline_url}" class="btn btn-decline">❌ DECLINE</a>
        </div>
        
        <div class="footer">
            <p>VirtualJobGuru Social Automation System</p>
            <p>Click the buttons above to approve or decline this post.</p>
        </div>
    </div>
</body>
</html>
"""

msg.attach(MIMEText(html_body, 'html'))

# Attach video file
try:
    with open(VIDEO_PATH, 'rb') as f:
        video_data = f.read()
    
    video_attachment = MIMEBase('application', 'octet-stream')
    video_attachment.set_payload(video_data)
    encoders.encode_base64(video_attachment)
    video_attachment.add_header('Content-Disposition', f'attachment; filename="test_video.mp4"')
    msg.attach(video_attachment)
    print(f"✅ Video attached: {os.path.basename(VIDEO_PATH)} ({len(video_data) / 1024 / 1024:.2f} MB)")
except Exception as e:
    print(f"❌ Failed to attach video: {e}")
    sys.exit(1)

# Send email
try:
    print(f"\n📧 Sending approval email...")
    print(f"   From: {smtp_settings['sender_email']}")
    print(f"   To: {smtp_settings['recipient_email']}")
    print(f"   Subject: {msg['Subject']}")
    
    server = smtplib.SMTP(smtp_settings['smtp_server'], int(smtp_settings['smtp_port']))
    server.starttls()
    server.login(smtp_settings['sender_email'], smtp_settings['app_password'])
    server.send_message(msg)
    server.quit()
    
    print("\n✅ Email sent successfully!")
    print(f"\n📋 Approval URLs:")
    print(f"   ✅ Approve: {approve_url}")
    print(f"   ❌ Decline: {decline_url}")
    
except Exception as e:
    print(f"\n❌ Failed to send email: {e}")
    sys.exit(1)
