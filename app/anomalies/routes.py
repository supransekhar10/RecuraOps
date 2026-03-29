from flask import Blueprint, render_template, request
from firebase_admin import db
from app.auth.middleware import require_auth

anomalies_bp = Blueprint('anomalies', __name__)


@anomalies_bp.route('/anomalies')
@require_auth
def list_anomalies():
    try:
        all_anomalies = db.reference('/recuraops/anomalies').get() or {}
        anomalies_list = sorted(
            [{'id': k, **v} for k, v in all_anomalies.items()],
            key=lambda x: x.get('detected_at', ''), reverse=True
        )
        filter_type = request.args.get('type', 'all')
        filter_severity = request.args.get('severity', 'all')
        filter_status = request.args.get('status', 'all')

        filtered = anomalies_list
        if filter_type != 'all':
            filtered = [a for a in filtered if a.get('type') == filter_type]
        if filter_severity != 'all':
            filtered = [a for a in filtered if a.get('severity') == filter_severity]
        if filter_status != 'all':
            filtered = [a for a in filtered if a.get('status') == filter_status]

        return render_template('anomalies/list.html', anomalies=filtered,
                               filter_type=filter_type, filter_severity=filter_severity,
                               filter_status=filter_status, active_page='anomalies')
    except Exception as e:
        return render_template('anomalies/list.html', anomalies=[], filter_type='all',
                               filter_severity='all', filter_status='all',
                               active_page='anomalies', error=str(e))


@anomalies_bp.route('/anomalies/<anomaly_id>')
@require_auth
def detail(anomaly_id):
    try:
        anomaly = db.reference(f'/recuraops/anomalies/{anomaly_id}').get()
        if not anomaly:
            return render_template('anomalies/detail.html', anomaly=None,
                                   active_page='anomalies', error='Anomaly not found')
        anomaly['id'] = anomaly_id
        return render_template('anomalies/detail.html', anomaly=anomaly, active_page='anomalies')
    except Exception as e:
        return render_template('anomalies/detail.html', anomaly=None,
                               active_page='anomalies', error=str(e))
