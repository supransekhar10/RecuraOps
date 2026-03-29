from flask import Blueprint, jsonify
from firebase_admin import db
from app.auth.middleware import require_auth
from app.agents import agent_status

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/kpi')
@require_auth
def kpi():
    try:
        data = db.reference('/recuraops/kpi_summary').get() or {}
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/anomalies')
@require_auth
def anomalies():
    try:
        all_ano = db.reference('/recuraops/anomalies').get() or {}
        result = sorted([{'id': k, **v} for k, v in all_ano.items()],
                        key=lambda x: x.get('detected_at', ''), reverse=True)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/run-scan', methods=['POST'])
@require_auth
def run_scan():
    try:
        import threading
        from app.agents.monitoring_agent import MonitoringAgent
        threading.Thread(target=MonitoringAgent().run, daemon=True).start()
        return jsonify({'success': True, 'message': 'Scan triggered in background'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/agent-status')
@require_auth
def get_agent_status():
    return jsonify({'success': True, 'data': agent_status})
