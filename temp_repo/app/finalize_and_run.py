import json
import base64
import os
import subprocess

# Credentials data provided by user
raw_pk = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDqpI0UaqM7JnIK
asLaQjJkT9QaBSsgRvzKr9XkfRqMVrPQ3JzAIfZcpLDO2gexENZvfW2YJf3DfTE3
4UPn+Jml8ZH0nLJBqfk79J2EEYGmKeH8TmbUNF9RngGn2xmu+2HbmTFaTCsvrZJM
/N977gX2AEIQVUN+GvfRGmjnrdM20MNl8xMrjfU9UKXYEhAa9R6MEjyrDXx/fDyU
CD2gF8BPuyytL/sywh73vQbwuGTR+g89XtinfHsuzn2ygo8cUS3RaR92iJwAdWNY
arSWUwLyeycBR+EN3IFppH/QDijnvJmrL19R3DJrS191BSkV68JxC508SSp6f4un
6GFyb62DAgMBAAECggEAJoxKBnn5FGqd1ErzIAWStHAjmZ1nwbG9Lf9H1csdEBkz
ntAh0/WDsUblXYrmRsevg5AgTIn/QpMvDHjm1J5Lr4HCYreW1qJv9WiA3EHoKdqXt
fmnS8uHNFwzXm3VJ+Y6gO6zQiCkjSdNAycJxZLFslpw26OquX9/w/o/8KV5L6MvV
TaF18fMwUv9w48K7uvfusvIGH/3Q5t7EfO0M0W8pUZYHA60mW8SVhZzKIHzgyxex
sVxCQFFdTpe3o80Vnj5q1iRTF4OoC0Oxdy+NhQ8vfDO0ixbe+DujhJOBhHoXoq9x
ngWWir/IC+y2CxCofib9aYHFo7K923qvbjXA20GPoQKBgQD+Xr9rTvu9CmM1JK4/
UsfS6atjJLxXl97/j3+zFJT16/XmYY47B4q0yMxOXC1LXnJKiqOauWNgbY+jPGVz
pszUc6cRa5LQzHior94WhUo1pKHWThTjkyaUoGclEAboWwQhUtCU3OYumr4T7Kuq
YNcy3G1pkjGI51er7va12o2KDwKBgQDsJXGlDdeQFylUWIHJawrLfJhH1YsrtFvR
reqerjnXJe8bpXk/4KUbghrscoSqPRXHNZX3+uIoGk5Vq3vlhFJDw2rHiiZXWuSN
45ZdeTFmeY34wOCDklzAPRK6VZyBlddXZyGHFJe6TYm6sBqjiuVt3mDIOG3DKJ8a
MVrRpPNpTQKBgQCy7sluXegdqbHxzzS3nK6uAeuq2UuXvmCCm1n0CjVi7LJUdimM
Apki5OE6+gJusyhooS/HBkQOr+NLq4+eFCagCB7s1SQ4tqzl1JjAdNCn/YBOdSyi
jX+lK1SDMMv7JRM5sbzCCsXs4LN25pQ3TNn0kDRzAADSUhJNAtMPR4crJwKBgGdn
9h3Ks+w62DRBFYQ3xWBZzO0Xy3t13QcyWxzlOhrGV7AJg9C+9E3ZaSTE+Ob7HMBA
7MzMJaBd9JN7JiPZD5Twy59ZFXUHLjIbyMphuYogDFUzUJ0MyGS92aeSuZfdH5D8
bigSkmZYcck4OFIJDnJQAJ1saFQfQ5xapGRNEPG5AoGBAMy060XNW53UdQ7WF7rZ
63lGA47UJDsbqZlzhLEOwMm0onTbbvL+mw+bFy57Opgbj/t7gk/nYAayMzio6KMV
0OBrHnIlxbnyYyoZ9osUZL6vFPe4tJgKpriD4J4is8+W9oiBEN99V7bvorx3J8eX
v9qPgcysRyb0Ew76KEeq6AgA
-----END PRIVATE KEY-----"""

# Clean up PK
lines = raw_pk.strip().split("\n")
header = lines[0]
footer = lines[-1]
b64 = "".join(lines[1:-1]).replace(" ", "").replace("\r", "")

# Fix padding
while len(b64) % 4 != 0:
    b64 += "="

# Reformat
formatted_b64 = "\n".join([b64[i:i+64] for i in range(0, len(b64), 64)])
final_pk = f"{header}\n{formatted_b64}\n{footer}\n"

# JSON Structure
creds_dict = {
  "type": "service_account",
  "project_id": "julia-ai-automation",
  "private_key_id": "15b0042e3f6bccc0bc27afc86576920a4a606e25",
  "private_key": final_pk,
  "client_email": "vertex-express@julia-ai-automation.iam.gserviceaccount.com",
  "client_id": "111908137455175711030",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vertex-express%40julia-ai-automation.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Write file
creds_path = "/root/.gemini/antigravity/scratch/social_automato/app/google_credentials.json"
with open(creds_path, "w") as f:
    json.dump(creds_dict, f, indent=2)

print(f"✅ Credentials written to {creds_path}")

# Verify
try:
    from google.oauth2 import service_account
    service_account.Credentials.from_service_account_file(creds_path)
    print("✅ Credentials verified by SDK")
except Exception as e:
    print(f"❌ SDK verification failed: {e}")
    exit(1)

# Run video generation script
script_path = "/root/.gemini/antigravity/scratch/social_automato/app/generate_julia_branded.py"
print(f"🚀 Running {script_path}...")
subprocess.run(["python3", script_path], check=True)
