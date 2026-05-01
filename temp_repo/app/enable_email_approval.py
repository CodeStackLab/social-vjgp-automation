#!/usr/bin/env python3
"""
Enable Email Approval Workflow
This script enables the SMTP-based email approval system so posts require Gmail approval before publishing.
"""

import json
import os

CONFIG_FILE = "/app/data/app_settings.json"

def enable_email_approval():
    """Enable SMTP email approval in the application settings"""
    
    print("=" * 70)
    print("🔧 ENABLING EMAIL APPROVAL WORKFLOW")
    print("=" * 70)
    
    # Load existing config
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found at {CONFIG_FILE}")
        return
    
    print(f"📂 Loading config from {CONFIG_FILE}")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Show current SMTP status
    current_smtp = config.get("smtp_settings", {})
    current_status = current_smtp.get("enabled", False)
    print(f"\n📊 Current SMTP Status: {'ENABLED ✅' if current_status else 'DISABLED ❌'}")
    
    # Ensure smtp_settings exists
    if "smtp_settings" not in config:
        config["smtp_settings"] = {}
    
    # Enable SMTP
    config["smtp_settings"]["enabled"] = True
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Email approval workflow has been ENABLED")
    print("=" * 70)
    print("\n📋 What this means:")
    print("   • Posts will now REQUIRE Gmail approval before publishing")
    print("   • Approval emails will be sent to:", current_smtp.get("recipient_email", "N/A"))
    print("   • Posts will NOT publish until you click 'Approve' in email")
    print("   • Content is queued and waits for your approval")
    print("\n🔄 Restart the application for changes to take effect:")
    print("   docker restart social_app")
    print("=" * 70)

if __name__ == "__main__":
    try:
        enable_email_approval()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
