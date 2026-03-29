"""seed_firebase.py — Seeds all demo data. Overwrites /recuraops."""
import json, os
from dotenv import load_dotenv
load_dotenv()
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS', 'firebase_service_account.json'))
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv('FIREBASE_DB_URL')})

with open('seed_data.json', encoding='utf-8') as f:
    seed = json.load(f)

db.reference('/recuraops').set(seed)
print('✅  RecuraOps demo data seeded successfully.')
print(f"   Anomalies: {len(seed['anomalies'])} | Approvals: {len(seed['approval_requests'])} | Actions: {len(seed['action_log'])}")
