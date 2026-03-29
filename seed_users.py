"""
seed_users.py — Creates Firebase Auth users via Admin SDK.
Run once before seed_firebase.py.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS', 'firebase_service_account.json'))
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv('FIREBASE_DB_URL')})

DEMO_USERS = [
    {'email': 'admin@recuraops.io',    'password': 'RecuraAdmin@2025',    'display_name': 'Arjun Mehta'},
    {'email': 'analyst@recuraops.io',  'password': 'RecuraAnalyst@2025',  'display_name': 'Priya Rangan'},
    {'email': 'approver@recuraops.io', 'password': 'RecuraApprover@2025', 'display_name': 'Karthik Sundaram'},
]

for u in DEMO_USERS:
    try:
        existing = auth.get_user_by_email(u['email'])
        print(f'⚠️  Already exists: {u["email"]} (uid={existing.uid})')
    except auth.UserNotFoundError:
        user = auth.create_user(email=u['email'], password=u['password'],
                                display_name=u['display_name'], email_verified=True)
        print(f'✅  Created: {u["email"]} (uid={user.uid})')

print('\n✅  Firebase Auth users ready. Now run: python seed_firebase.py')
