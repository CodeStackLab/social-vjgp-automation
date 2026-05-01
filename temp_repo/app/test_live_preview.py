#!/usr/bin/env python3
"""
Test live preview in approval emails - Video and Image
"""
import os
import sys
sys.path.insert(0, '/app')

import json
import time
from main import send_approval_email, SMTP_SETTINGS

# Test 1: Video Post
video_post = {
    "title": "Top Interview Tips for 2026",
    "caption": """Master these essential interview techniques! 

🎯 Key Points:
- Research the company
- Practice STAR responses
- Ask thoughtful questions

#InterviewTips #CareerAdvice #JobSearch""",
    "platforms": ["Instagram"],
    "type": "Video Reel",
    "media_url": "https://vjgu.online/videos/videos/branded_random_1770140525.mp4"
}

# Test 2: Image Post
image_post = {
    "title": "Resume Mistakes to Avoid",
    "caption": """Don't let these common mistakes ruin your chances!

✅ Professional formatting
✅ Clear contact info
✅ Quantified achievements

#ResumeTips #CareerGrowth #JobHunting""",
    "platforms": ["LinkedIn"],
    "type": "Image Post",
    "media_url": "https://vjgu.online/videos/images/branded_post_1770197312.png"
}

print("\n🎬 Testing LIVE PREVIEW in approval emails...\n")

# Test Video
print("📧 Sending VIDEO approval email with live preview...")
video_id = f"video_test_{int(time.time())}"
if send_approval_email(video_post, video_id):
    print("✅ Video email sent!")
    print(f"   Preview URL: {video_post['media_url']}")
else:
    print("❌ Video email failed!")

time.sleep(2)

# Test Image
print("\n📧 Sending IMAGE approval email with live preview...")
image_id = f"image_test_{int(time.time())}"
if send_approval_email(image_post, image_id):
    print("✅ Image email sent!")
    print(f"   Preview URL: {image_post['media_url']}")
else:
    print("❌ Image email failed!")

print(f"\n📬 Check your inbox: {SMTP_SETTINGS.get('recipient_email')}")
print("\n🎯 Expected in emails:")
print("   - Video: Embedded player (click to play)")
print("   - Image: Live image preview (social media style)")
