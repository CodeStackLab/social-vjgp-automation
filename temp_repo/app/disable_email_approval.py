#!/usr/bin/env python3
"""
Disable Email Approval Workflow
This script disables the SMTP-based email approval system so posts publish immediately.
"""

import json
import os

CONFIG_FILE = "/app/data/app_settings.json"

def disable_email_approval():
    """Disable SMTP email approval in the application settings"""
    
    print("=" * 70)
    print("🔧 DISABLING EMAIL APPROVAL WORKFLOW")
    print("=" * 70)
    
    # Check if config file exists
    if not os.path.exists(CONFIG_FILE):
        print(f"⚠️  Config file not found at {CONFIG_FILE}")
        print("Creating new config with SMTP disabled...")
        config = {
            "smtp_settings": {
                "enabled": False
            }
        }
    else:
        # Load existing config
        print(f"📂 Loading config from {CONFIG_FILE}")
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Show current SMTP status
        current_smtp = config.get("smtp_settings", {})
        current_status = current_smtp.get("enabled", False)
        print(f"\n📊 Current SMTP Status: {'ENABLED ✅' if current_status else 'DISABLED ❌'}")
        
        if current_status:
            print("\n🔄 Email approval is currently ENABLED")
            print("   Posts are being sent to Gmail for approval before publishing")
        else:
            print("\n✅ Email approval is already DISABLED")
            print("   Posts publish immediately without approval")
    
    # Ensure smtp_settings exists
    if "smtp_settings" not in config:
        config["smtp_settings"] = {}
    
    # Disable SMTP
    config["smtp_settings"]["enabled"] = False
    
    # Save config
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Email approval workflow has been DISABLED")
    print("=" * 70)
    print("\n📋 What this means:")
    print("   • Posts will now publish IMMEDIATELY without email approval")
    print("   • No Gmail notifications will be sent")
    print("   • Content goes directly to social media platforms")
    print("\n💡 To re-enable email approval:")
    print("   • Go to Settings → Gmail SMTP Notifications in the web UI")
    print("   • Or set 'enabled': true in smtp_settings")
    print("\n🔄 Restart the application for changes to take effect:")
    print("   docker-compose restart")
    print("=" * 70)

if __name__ == "__main__":
    try:
        disable_email_approval()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
