import os
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import firebase_admin.auth as fb_auth
from firebase_admin import db

auth_bp = Blueprint('auth', __name__)


def _firebase_web_config():
    return {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.getenv('FIREBASE_DB_URL'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID'),
    }


@auth_bp.route('/login', methods=['GET'])
def login():
    if session.get('firebase_token'):
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html', firebase_config=_firebase_web_config())


@auth_bp.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    id_token = data.get('idToken') if data else None
    if not id_token:
        return jsonify({'success': False, 'error': 'No token provided'}), 400
    try:
        decoded = fb_auth.verify_id_token(id_token)
        uid = decoded['uid']
        email = decoded.get('email', '')
        session['firebase_token'] = id_token
        session['user_uid'] = uid
        session['user_email'] = email
        try:
            all_users = db.reference('/recuraops/users').get() or {}
            matched = next((u for u in all_users.values() if u.get('email') == email), None)
            if matched:
                session['user_name'] = matched.get('name', email.split('@')[0].title())
                session['user_role'] = matched.get('role', 'analyst')
                session['user_designation'] = matched.get('designation', '')
                session['user_initials'] = matched.get('avatar_initials', email[:2].upper())
            else:
                session['user_name'] = email.split('@')[0].title()
                session['user_role'] = 'analyst'
                session['user_designation'] = ''
                session['user_initials'] = email[:2].upper()
        except Exception:
            session['user_name'] = email.split('@')[0].title()
            session['user_role'] = 'analyst'
            session['user_initials'] = email[:2].upper()
        return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid credentials. Please try again.'}), 401


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
