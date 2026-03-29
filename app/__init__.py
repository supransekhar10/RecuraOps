import os
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:
        cred_path = os.getenv('FIREBASE_CREDENTIALS', 'firebase_service_account.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DB_URL')
        })

    @app.template_filter('inr')
    def format_inr(value):
        try:
            value = int(value)
            s = str(abs(value))
            if len(s) <= 3:
                return f'₹{s}'
            result = s[-3:]
            s = s[:-3]
            while len(s) > 2:
                result = s[-2:] + ',' + result
                s = s[:-2]
            if s:
                result = s + ',' + result
            return f'₹{result}'
        except Exception:
            return f'₹{value}'

    @app.template_filter('timeago')
    def time_ago(value):
        from datetime import datetime, timezone
        try:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                return ''
            now = datetime.now(timezone.utc)
            s = (now - dt).total_seconds()
            if s < 60:
                return 'just now'
            elif s < 3600:
                return f'{int(s/60)}m ago'
            elif s < 86400:
                return f'{int(s/3600)}h ago'
            else:
                return f'{int(s/86400)}d ago'
        except Exception:
            return str(value)

    @app.template_filter('dateformat')
    def format_date(value, fmt='%d %b %Y, %H:%M'):
        from datetime import datetime
        try:
            if isinstance(value, str):
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(fmt)
            return value
        except Exception:
            return str(value)

    @app.context_processor
    def inject_globals():
        from app.agents import agent_status
        return {
            'current_user': {
                'name': session.get('user_name', 'User'),
                'email': session.get('user_email', ''),
                'role': session.get('user_role', 'analyst'),
                'initials': session.get('user_initials', 'U'),
                'designation': session.get('user_designation', ''),
            },
            'agent_status': agent_status,
        }

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.anomalies.routes import anomalies_bp
    from app.approvals.routes import approvals_bp
    from app.actions.routes import actions_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(anomalies_bp)
    app.register_blueprint(approvals_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        _start_scheduler()

    return app


def _start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from app.agents.monitoring_agent import MonitoringAgent
        from app.agents.action_agent import ActionAgent

        scheduler = BackgroundScheduler(daemon=True)
        interval_min = int(os.getenv('AGENT_SCAN_INTERVAL_MINUTES', 5))
        poll_min = int(os.getenv('ACTION_POLL_INTERVAL_MINUTES', 2))

        scheduler.add_job(MonitoringAgent().run, 'interval', minutes=interval_min,
                          id='monitoring_agent', max_instances=1)
        scheduler.add_job(ActionAgent().poll_and_execute, 'interval', minutes=poll_min,
                          id='action_agent', max_instances=1)
        scheduler.start()
        print(f'✅  RecuraOps Scheduler started (scan:{interval_min}m | action:{poll_min}m)')
    except Exception as e:
        print(f'⚠️  Scheduler failed to start: {e}')
