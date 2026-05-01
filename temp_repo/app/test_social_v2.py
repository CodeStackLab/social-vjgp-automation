#!/usr/bin/env python3
"""
Test Fixed Social Image Generator
"""

import sys
sys.path.insert(0, '/app')

import social_image_v2

# Client details
client_details = {
    "contact_info": {
        "website": "www.virtualjobguru.com",
        "email": "info@virtualjobguru.com",
        "phone": "+49 1577 4331858"
    }
}

print("Testing FIXED Social Post Generation...")
print("="*70)

# Generate test image
result = social_image_v2.generate_social_post_v2(
    topic="Interview Success Tips",
    subtitle="Professional guidance for career growth",
    client_details=client_details,
    platform="instagram"
)

if result:
    print(f"\n✅ Test successful! Image saved to: {result}")
else:
    print("\n❌ Test failed!")
