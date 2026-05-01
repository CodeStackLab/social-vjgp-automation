import json
import base64
import os

path = "/root/.gemini/antigravity/scratch/social_automato/app/google_credentials.json"
if os.path.exists(path):
    with open(path) as f:
        creds = json.load(f)
    pk = creds["private_key"]
    parts = pk.strip().split("\n")
    header = parts[0]
    footer = parts[-1]
    # Clean up base64 part: remove escaped newlines and actual newlines
    b64 = "".join(parts[1:-1]).replace("\\n", "").replace("\n", "").strip()
    
    print(f"Original Base64 length: {len(b64)}")
    
    # Add padding if needed
    while len(b64) % 4 != 0:
        b64 += "="
        
    print(f"Padded Base64 length: {len(b64)}")
    
    try:
        decoded = base64.b64decode(b64)
        print("✅ Base64 is valid and decodable")
        # Format back to 64-char lines
        formatted_b64 = "\n".join([b64[i:i+64] for i in range(0, len(b64), 64)])
        creds["private_key"] = f"{header}\n{formatted_b64}\n{footer}\n"
        with open(path, "w") as f:
            json.dump(creds, f, indent=2)
        print("✅ Corrected google_credentials.json")
    except Exception as e:
        print(f"❌ Failed to decode: {e}")
else:
    print(f"❌ File not found: {path}")
