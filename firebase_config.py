import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Option 1: Get credentials from a JSON string in an environment variable (for deployment)
cred_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")

if cred_json_str:
    try:
        cred_info = json.loads(cred_json_str)
        cred = credentials.Certificate(cred_info)
    except json.JSONDecodeError:
        raise ValueError("Failed to decode JSON from GOOGLE_CREDENTIALS_JSON.")
# Option 2: Fallback to path for local development
else:
    cred_path = os.getenv("SERVICE_ACCOUNT_KEY_PATH")
    if not cred_path:
        raise ValueError("Set either the GOOGLE_CREDENTIALS_JSON or the SERVICE_ACCOUNT_KEY_PATH environment variable.")
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Service account key file not found at: {cred_path}")
        
    cred = credentials.Certificate(cred_path)

# Initialize Firebase
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    
db = firestore.client()
