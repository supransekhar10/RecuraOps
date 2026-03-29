from flask import Blueprint, render_template
from firebase_admin import db
from app.auth.middleware import require_auth
from app.agents import agent_status

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@require_auth
def index():
    try:
        kpi = db.reference('/recuraops/kpi_summary').get() or {}
        all_anomalies = db.reference('/recuraops/anomalies').get() or {}
        action_log = db.reference('/recuraops/action_log').get() or {}

        anomalies_list = sorted(
            [{'id': k, **v} for k, v in all_anomalies.items()],
            key=lambda x: x.get('detected_at', ''), reverse=True
        )
        recent_anomalies = anomalies_list[:6]

        savings_breakdown = {'Duplicate Invoices': 0, 'Unused SaaS': 0, 'Idle Cloud': 0}
        for act in action_log.values():
            if act.get('status') == 'completed':
                amt = act.get('savings_realized_annual', 0)
                atype = act.get('action', '')
                if atype == 'block_payment':
                    savings_breakdown['Duplicate Invoices'] += amt
                elif atype == 'cancel_licenses':
                    savings_breakdown['Unused SaaS'] += amt
                elif atype == 'shutdown_resource':
                    savings_breakdown['Idle Cloud'] += amt

        if sum(savings_breakdown.values()) == 0:
            for ano in all_anomalies.values():
                amt = ano.get('financial_impact_annual', 0)
                t = ano.get('type', '')
                if 'duplicate' in t:
                    savings_breakdown['Duplicate Invoices'] += amt
                elif 'subscription' in t:
                    savings_breakdown['Unused SaaS'] += amt
                elif 'cloud' in t or 'idle' in t:
                    savings_breakdown['Idle Cloud'] += amt

        return render_template('dashboard/index.html', kpi=kpi, recent_anomalies=recent_anomalies,
                               agent_status=agent_status, savings_breakdown=savings_breakdown,
                               active_page='dashboard')
    except Exception as e:
        return render_template('dashboard/index.html', kpi={}, recent_anomalies=[],
                               agent_status=agent_status,
                               savings_breakdown={'Duplicate Invoices': 0, 'Unused SaaS': 0, 'Idle Cloud': 0},
                               active_page='dashboard', error=str(e))
