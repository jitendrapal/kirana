import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

cred = None

# Option 1: Credentials from environment variable (JSON string) - Recommended for deployment
google_credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if google_credentials_json:
    try:
        service_account_info = json.loads(google_credentials_json)
        cred = credentials.Certificate(service_account_info)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding GOOGLE_CREDENTIALS_JSON: {e}")

# Option 2: Credentials from file path in environment variable - for local development
if not cred:
    service_account_key_path = os.environ.get("SERVICE_ACCOUNT_KEY_PATH")
    if service_account_key_path:
        if not os.path.exists(service_account_key_path):
            raise FileNotFoundError(f"Service account key file not found at path: {service_account_key_path}")
        cred = credentials.Certificate(service_account_key_path)

# If no credentials found, provide clear instructions
if not cred:
    error_message = """
    --- Firebase Admin SDK Initialization Error ---
    Could not find Firebase credentials. Please configure them in one of the following ways:

    1. For Deployment (Recommended):
       Set the `GOOGLE_CREDENTIALS_JSON` environment variable to the JSON content of your service account key.

    2. For Local Development:
       - Create a `.env` file in the root of your project.
       - Add the following line to the `.env` file:
         SERVICE_ACCOUNT_KEY_PATH=/path/to/your/serviceAccountKey.json
       - Make sure the path is correct.

    You can get your service account key from the Firebase console:
    Project Settings > Service accounts > Generate new private key
    """
    raise ValueError(error_message)


# Initialize the Firebase app (if not already initialized)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()
