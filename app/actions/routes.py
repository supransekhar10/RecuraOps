from flask import Blueprint, render_template
from firebase_admin import db
from app.auth.middleware import require_auth

actions_bp = Blueprint('actions', __name__)


@actions_bp.route('/actions')
@require_auth
def log():
    try:
        action_log = db.reference('/recuraops/action_log').get() or {}
        actions_list = sorted(
            [{'id': k, **v} for k, v in action_log.items()],
            key=lambda x: x.get('timestamp', ''), reverse=True
        )
        total_savings_annual = sum(
            a.get('savings_realized_annual', 0) for a in actions_list if a.get('status') == 'completed')
        total_savings_monthly = sum(
            a.get('savings_realized_monthly', 0) for a in actions_list if a.get('status') == 'completed')
        return render_template('actions/log.html', actions=actions_list,
                               total_savings_annual=total_savings_annual,
                               total_savings_monthly=total_savings_monthly,
                               active_page='actions')
    except Exception as e:
        return render_template('actions/log.html', actions=[], total_savings_annual=0,
                               total_savings_monthly=0, active_page='actions', error=str(e))
