import json

key_lines = [
    "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDqpI0UaqM7JnIK",
    "asLaQjJkT9QaBSsgRvzKr9XkfRqMVrPQ3JzAIfZcpLDO2gexENZvfW2YJf3DfTE3",
    "4UPn+Jml8ZH0nLJBqfk79J2EEYGmKeH8TmbUNF9RngGn2xmu+2HbmTFaTCsvrZJM",
    "/N977gX2AEIQVUN+GvfRGmjnrdM20MNl8xMrjfU9UKXYEhAa9R6MEjyrDXx/fDyU",
    "CD2gF8BPuyytL/sywh73vQbwuGTR+g89XtinfHsuzn2ygo8cUS3RaR92iJwAdWNY",
    "arSWUwLyeycBR+EN3IFppH/QDijnvJmrL19R3DJrS191BSkV68JxC508SSp6f4un",
    "6GFyb62DAgMBAAECggEAJoxKBnn5FGqd1ErzIAWStHAjmZ1nwbG9Lf9H1csdEBkz",
    "tAh0/WDsUblXYrmRsevg5AgTIn/QpMvDHjm1J5Lr4HCYreW1qJv9WiA3EHoKdqXt",
    "fmnS8uHNFwzXm3VJ+Y6gO6zQiCkjSdNAycJxZLFslpw26OquX9/w/o/8KV5L6MvV",
    "TaF18fMwUv9w48K7uvfusvIGH/3Q5t7EfO0M0W8pUZYHA60mW8SVhZzKIHzgyxex",
    "sVxCQFFdTpe3o80Vnj5q1iRTF4OoC0Oxdy+NhQ8vfDO0ixbe+DujhJOBhHoXoq9x",
    "ngWWir/IC+y2CxCofib9aYHFo7K923qvbjXA20GPoQKBgQD+Xr9rTvu9CmM1JK4/",
    "UsfS6atjJLxXl97/j3+zFJT16/XmYY47B4q0yMxOXC1LXnJKiqOauWNgbY+jPGVz",
    "pszUc6cRa5LQzHior94WhUo1pKHWThTjkyaUoGclEAboWwQhUtCU3OYumr4T7Kuq",
    "YNcy3G1pkjGI51er7va12o2KDwKBgQDsJXGlDdeQFylUWIHJawrLfJhH1YsrtFvR",
    "reqerjnXJe8bpXk/4KUbghrscoSqPRXHNZX3+uIoGk5Vq3vlhFJDw2rHiiZXWuSN",
    "45ZdeTFmeY34wOCDklzAPRK6VZyBlddXZyGHFJe6TYm6sBqjiuVt3mDIOG3DKJ8a",
    "MVrRpPNpTQKBgQCy7sluXegdqbHxzzS3nK6uAeuq2UuXvmCCm1n0CjVi7LJUdimM",
    "Apki5OE6+gJusyhooS/HBkQOr+NLq4+eFCagCB7s1SQ4tqzl1JjAdNCn/YBOdSyi",
    "jX+lK1SDMMv7JRM5sbzCCsXs4LN25pQ3TNn0kDRzAADSUhJNAtMPR4crJwKBgGdn",
    "9h3Ks+w62DRBFYQ3xWBZzO0Xy3t13QcyWxzlOhrGV7AJg9C+9E3ZaSTE+Ob7HMBA",
    "7MzMJaBd9JN7JiPZD5Twy59ZFXUHLjIbyMphuYogDFUzUJ0MyGS92aeSuZfdH5D8",
    "bigSkmZYcck4OFIJDnJQAJ1saFQfQ5xapGRNEPG5AoGBAMy060XNW53UdQ7WF7rZ",
    "63lGA47UJDsbqZlzhLEOwMm0onTbbvL+mw+bFy57Opgbj/t7gk/nYAayMzio6KMV",
    "0OBrHnIlxbnyYyoZ9osUZL6vFPe4tJgKpriD4J4is8+W9oiBEN99V7bvorx3J8eX",
    "v9qPgcysRyb0Ew76KEeq6AgA"
]

b64 = "".join(key_lines)
# Standard PEM formatting: header, 64-char lines, footer
formatted_b64 = "\n".join([b64[i:i+64] for i in range(0, len(b64), 64)])
private_key = f"-----BEGIN PRIVATE KEY-----\n{formatted_b64}\n-----END PRIVATE KEY-----\n"

creds = {
  "type": "service_account",
  "project_id": "julia-ai-automation",
  "private_key_id": "15b0042e3f6bccc0bc27afc86576920a4a606e25",
  "private_key": private_key,
  "client_email": "vertex-express@julia-ai-automation.iam.gserviceaccount.com",
  "client_id": "111908137455175711030",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vertex-express%40julia-ai-automation.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

with open("/root/.gemini/antigravity/scratch/social_automato/app/google_credentials.json", "w") as f:
    json.dump(creds, f, indent=2)

print("✅ Credentials file written.")
