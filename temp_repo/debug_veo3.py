#!/usr/bin/env python3
"""
Debug Veo 3 operation result structure
"""

import sys
import os
sys.path.insert(0, '/root/.gemini/antigravity/scratch/social_automato/app')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/google_credentials.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

import time
from google import genai
from google.genai.types import GenerateVideosConfig

client = genai.Client(vertexai=True, project='your-project-id', location='us-central1')

print("Creating operation...")
operation = client.models.generate_videos(
    model="veo-3.1-fast-generate-001",
    prompt="a simple test video",
    config=GenerateVideosConfig(aspect_ratio='9:16'),
)

print(f"Operation: {operation.name}")
print(f"Waiting for completion...")

while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)
    print(f"  Polling... done={operation.done}")

print(f"\nOperation complete!")
print(f"\nDEBUG - Operation attributes:")
print(f"  dir(operation): {[x for x in dir(operation) if not x.startswith('_')]}")
print(f"\n  operation.done: {operation.done}")
print(f"  operation.result: {operation.result}")
print(f"  type(operation.result): {type(operation.result)}")

if operation.result:
    print(f"\n  dir(operation.result): {[x for x in dir(operation.result) if not x.startswith('_')]}")
    
    if hasattr(operation.result, 'generated_videos'):
        print(f"\n  operation.result.generated_videos: {operation.result.generated_videos}")
        
        if operation.result.generated_videos:
            video = operation.result.generated_videos[0]
            print(f"\n  type(video): {type(video)}")
            print(f"  dir(video): {[x for x in dir(video) if not x.startswith('_')]}")
            
            if hasattr(video, 'video'):
                print(f"\n  type(video.video): {type(video.video)}")
                print(f"  dir(video.video): {[x for x in dir(video.video) if not x.startswith('_')]}")
                
                if hasattr(video.video, 'data'):
                    print(f"\n  video.video.data exists: {video.video.data is not None}")
                    if video.video.data:
                        print(f"  len(video.video.data): {len(video.video.data)}")
                
                if hasattr(video.video, 'uri'):
                    print(f"\n  video.video.uri: {video.video.uri}")
