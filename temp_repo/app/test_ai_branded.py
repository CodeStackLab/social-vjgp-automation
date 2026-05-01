#!/usr/bin/env python3
"""
Test AI-Generated Branded Images
"""

import sys
sys.path.insert(0, '/app')

import ai_branded_images

# Client details
client_details = {
    "contact_info": {
        "website": "www.virtualjobguru.com",
        "email": "info@virtualjobguru.com",
        "phone": "+49 1577 4331858"
    }
}

print("Testing AI-Generated Branded Post...")
print("="*70)

# Generate test image
result = ai_branded_images.generate_ai_branded_post(
    topic="Interview Success Tips",
    subtitle="Professional guidance for career growth",
    client_details=client_details,
    platform="instagram",
    logo_size="small"  # Small logo in corner
)

if result:
    print(f"\n✅ Test successful! Image saved to: {result}")
else:
    print("\n❌ Test failed!")
