#!/usr/bin/env python3
"""
Test GCS bucket creation and video extension
"""

import sys
import os
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'

from google.cloud import storage

PROJECT_ID = "your-project-id"
BUCKET_NAME = "vjgu-video-generation"
LOCATION = "us-central1"

def create_bucket_if_not_exists():
    """Create GCS bucket if it doesn't exist"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        
        # Check if bucket exists
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
            print(f"✅ Bucket already exists: gs://{BUCKET_NAME}")
            return True
        except:
            # Create bucket
            bucket = storage_client.create_bucket(
                BUCKET_NAME,
                location=LOCATION
            )
            print(f"✅ Created bucket: gs://{BUCKET_NAME}")
            return True
            
    except Exception as e:
        print(f"❌ Bucket error: {e}")
        return False

if __name__ == "__main__":
    print("Testing GCS bucket setup...")
    create_bucket_if_not_exists()
