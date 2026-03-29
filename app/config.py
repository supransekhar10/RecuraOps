import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'fallback-secret')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'firebase_service_account.json')
    FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_WEB_CONFIG = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.getenv('FIREBASE_DB_URL'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID'),
    }
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 1000))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.3))
    AGENT_SCAN_INTERVAL_MINUTES = int(os.getenv('AGENT_SCAN_INTERVAL_MINUTES', 5))
    ACTION_POLL_INTERVAL_MINUTES = int(os.getenv('ACTION_POLL_INTERVAL_MINUTES', 2))
    IDLE_CPU_THRESHOLD_PCT = float(os.getenv('IDLE_CPU_THRESHOLD_PCT', 5))
    IDLE_DAYS_THRESHOLD = int(os.getenv('IDLE_DAYS_THRESHOLD', 14))
    SUBSCRIPTION_UTILIZATION_THRESHOLD_PCT = float(os.getenv('SUBSCRIPTION_UTILIZATION_THRESHOLD_PCT', 15))
    AUTO_ACTION_LIMIT_INR = float(os.getenv('AUTO_ACTION_LIMIT_INR', 10000))
