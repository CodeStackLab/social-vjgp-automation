#!/usr/bin/env python3
"""
Test Image Post Generation
"""

import sys
sys.path.insert(0, '/app')

import image_post_generator

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
    "Resume Writing Guide",
    "Career Growth Strategies",
    "Professional Networking"
]

print("Testing Image Post Generation...")
print("="*70)

# Generate one test image
result = image_post_generator.generate_branded_image_post(
    topic=topics[0],
    client_details=client_details,
    add_logo=True,
    add_contact=True
)

if result:
    print(f"\n✅ Test successful! Image saved to: {result}")
else:
    print("\n❌ Test failed!")
