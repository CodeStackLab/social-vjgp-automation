#!/usr/bin/env python3
"""
Test which Gemini models are available
"""

import requests
import json

API_KEY = "AIzaSyCKB14XMKDc0EXdotowzOhfWOfydYsojKA"

# Try different model endpoints
models_to_test = [
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-flash",
    "models/gemini-pro",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash"
]

print("Testing Gemini API models...")
print("="*70)

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say hello"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {model} - WORKING")
            data = response.json()
            if 'candidates' in data:
                result = data['candidates'][0]['content']['parts'][0]['text']
                print(f"   Response: {result[:50]}...")
        elif response.status_code == 404:
            print(f"❌ {model} - NOT FOUND (404)")
        else:
            print(f"⚠️  {model} - Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ {model} - Exception: {str(e)[:50]}")

print("="*70)
print("\nTesting list models endpoint...")

# Try to list available models
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
try:
    response = requests.get(list_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Available models:")
        for model in data.get('models', [])[:10]:
            print(f"  - {model.get('name', 'Unknown')}")
    else:
        print(f"❌ List models failed: {response.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")
