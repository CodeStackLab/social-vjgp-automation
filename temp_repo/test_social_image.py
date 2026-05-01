#!/usr/bin/env python3
"""
Test Professional Social Media Image Generation
"""

import sys
sys.path.insert(0, '/app')

import social_image_generator

# Client details
client_details = {
    "contact_info": {
        "website": "www.virtualjobguru.com",
        "email": "info@virtualjobguru.com",
        "phone": "+49 1577 4331858"
    }
}

# Test topics
topics = [
    "Interview Success Tips",
    "Beat ATS Filters",
    "Why Interviews Fail"
]

print("Testing Professional Social Post Generation...")
print("="*70)

# Generate test image for Instagram
result = social_image_generator.generate_social_post(
    topic=topics[0],
    client_details=client_details,
    platform="instagram",
    use_ai_background=False  # Use solid color for faster test
)

if result:
    print(f"\n✅ Test successful! Image saved to: {result}")
else:
    print("\n❌ Test failed!")
