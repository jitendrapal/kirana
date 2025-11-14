import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the path to the service account key file from an environment variable.
# The environment variable should be set to the full path of the servicekey.json file.
cred_path = os.getenv("SERVICE_ACCOUNT_KEY_PATH") 

if not cred_path:
    raise ValueError("The SERVICE_ACCOUNT_KEY_PATH environment variable is not set.")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
