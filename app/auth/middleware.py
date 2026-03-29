from functools import wraps
from flask import session, redirect, url_for
import firebase_admin.auth as fb_auth


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('firebase_token')
        if not token:
            return redirect(url_for('auth.login'))
        try:
            decoded = fb_auth.verify_id_token(token)
            session['user_uid'] = decoded['uid']
            session['user_email'] = decoded.get('email', '')
        except Exception:
            session.clear()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
