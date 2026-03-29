from datetime import datetime, timezone
from flask import Blueprint, render_template, request, session, jsonify
from firebase_admin import db
from app.auth.middleware import require_auth

approvals_bp = Blueprint('approvals', __name__)


@approvals_bp.route('/approvals')
@require_auth
def list_approvals():
    try:
        all_approvals = db.reference('/recuraops/approval_requests').get() or {}
        all_anomalies = db.reference('/recuraops/anomalies').get() or {}
        approvals_list = []
        for apr_id, apr_data in all_approvals.items():
            item = {'id': apr_id, **apr_data}
            ano_id = apr_data.get('anomaly_id')
            if ano_id and ano_id in all_anomalies:
                item['anomaly'] = {'id': ano_id, **all_anomalies[ano_id]}
            approvals_list.append(item)
        prio = {'high': 0, 'medium': 1, 'low': 2}
        approvals_list.sort(key=lambda x: (prio.get(x.get('priority', 'low'), 2), x.get('requested_at', '')))
        pending = [a for a in approvals_list if a.get('status') == 'pending']
        resolved = [a for a in approvals_list if a.get('status') != 'pending']
        return render_template('approvals/index.html', pending_approvals=pending,
                               resolved_approvals=resolved, active_page='approvals')
    except Exception as e:
        return render_template('approvals/index.html', pending_approvals=[],
                               resolved_approvals=[], active_page='approvals', error=str(e))


@approvals_bp.route('/approvals/<approval_id>/approve', methods=['POST'])
@require_auth
def approve(approval_id):
    try:
        apr_ref = db.reference(f'/recuraops/approval_requests/{approval_id}')
        apr_data = apr_ref.get()
        if not apr_data:
            return jsonify({'success': False, 'error': 'Approval not found'}), 404
        now = datetime.now(timezone.utc).isoformat()
        approver_email = session.get('user_email', 'unknown')
        apr_ref.update({'status': 'approved', 'approved_by': approver_email, 'approved_at': now})
        ano_id = apr_data.get('anomaly_id')
        if ano_id:
            db.reference(f'/recuraops/anomalies/{ano_id}').update(
                {'status': 'approved', 'approved_by': approver_email, 'approved_at': now})
        from app.agents.action_agent import ActionAgent
        ActionAgent().execute({'id': approval_id, **apr_data})
        return jsonify({'success': True, 'message': 'Approved and executed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@approvals_bp.route('/approvals/<approval_id>/reject', methods=['POST'])
@require_auth
def reject(approval_id):
    try:
        apr_ref = db.reference(f'/recuraops/approval_requests/{approval_id}')
        apr_data = apr_ref.get()
        if not apr_data:
            return jsonify({'success': False, 'error': 'Approval not found'}), 404
        now = datetime.now(timezone.utc).isoformat()
        apr_ref.update({'status': 'rejected', 'rejected_by': session.get('user_email'), 'rejected_at': now})
        ano_id = apr_data.get('anomaly_id')
        if ano_id:
            db.reference(f'/recuraops/anomalies/{ano_id}').update({'status': 'rejected'})
        return jsonify({'success': True, 'message': 'Action rejected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
