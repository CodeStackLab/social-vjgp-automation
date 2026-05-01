import os
try:
    from google import genai
    from google.genai import types
    
    project_id = "julia-ai-automation"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/.gemini/antigravity/scratch/social_automato/app/vertex-credentials.json"
    client = genai.Client(vertexai=True, project=project_id, location="us-central1")
    
    print("Listing Models...")
    for model in client.models.list():
        print(f"Model ID: {model.name}, Display Name: {model.display_name}")
except Exception as e:
    print(f"Error: {e}")
