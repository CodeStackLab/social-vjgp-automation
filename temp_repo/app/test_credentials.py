import os
import sys
from google.oauth2 import service_account
import google.auth.transport.requests

# Test credentials loading
credentials_path = 'vertex-credentials.json'
print(f'Testing credentials from: {credentials_path}')

try:
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    print('✓ Credentials loaded successfully')
    print(f'  Service Account: {credentials.service_account_email}')
    print(f'  Project ID: {credentials.project_id}')
    
    # Test token generation
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    print('✓ Access token generated successfully')
    print(f'  Token (first 50 chars): {credentials.token[:50]}...')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
