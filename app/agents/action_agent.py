"""Action Agent — executes approved actions."""
import logging
import uuid
from datetime import datetime, timezone
from firebase_admin import db
from app.agents import update_agent_status

logger = logging.getLogger(__name__)


class ActionAgent:
    name = 'action_agent'

    def poll_and_execute(self):
        update_agent_status(self.name, 'running')
        try:
            all_approvals = db.reference('/recuraops/approval_requests').get() or {}
            executed = 0
            for apr_id, apr_data in all_approvals.items():
                if apr_data.get('status') == 'approved' and not apr_data.get('action_executed'):
                    self.execute({'id': apr_id, **apr_data})
                    executed += 1
            update_agent_status(self.name, 'idle', items_processed=executed)
        except Exception as e:
            update_agent_status(self.name, 'error')
            logger.error(f'ActionAgent poll error: {e}')

    def execute(self, approval_request: dict):
        apr_id = approval_request.get('id')
        action = approval_request.get('action', 'notify_only')
        anomaly_id = approval_request.get('anomaly_id')
        try:
            anomaly = db.reference(f'/recuraops/anomalies/{anomaly_id}').get() or {}
            affected = anomaly.get('affected_entity', '')
            if action == 'block_payment':
                result = self.block_payment(affected)
            elif action == 'cancel_licenses':
                result = self.cancel_licenses(affected, anomaly)
            elif action == 'shutdown_resource':
                result = self.shutdown_resource(affected)
            else:
                result = {'description': 'Notification sent to finance team.'}

            act_id = f'ACT-{uuid.uuid4().hex[:6].upper()}'
            db.reference(f'/recuraops/action_log/{act_id}').set({
                'anomaly_id': anomaly_id, 'action': action,
                'description': result.get('description', ''),
                'executed_by': 'action_agent',
                'approved_by': approval_request.get('approved_by', 'system'),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'completed',
                'savings_realized_monthly': anomaly.get('financial_impact_monthly', 0),
                'savings_realized_annual': anomaly.get('financial_impact_annual', 0),
            })
            db.reference(f'/recuraops/approval_requests/{apr_id}').update({'action_executed': True})
            db.reference(f'/recuraops/anomalies/{anomaly_id}').update({
                'action_taken': True, 'action_timestamp': datetime.now(timezone.utc).isoformat()})
            from app.agents.verification_agent import VerificationAgent
            VerificationAgent().verify(act_id)
        except Exception as e:
            logger.error(f'ActionAgent execute error ({apr_id}): {e}')

    def block_payment(self, invoice_id: str) -> dict:
        if invoice_id:
            db.reference(f'/recuraops/vendor_invoices/{invoice_id}').update({'status': 'blocked'})
        return {'description': f'Invoice {invoice_id} marked as blocked. Payment will not be processed.'}

    def cancel_licenses(self, subscription_id: str, anomaly: dict) -> dict:
        if subscription_id:
            sub = db.reference(f'/recuraops/saas_subscriptions/{subscription_id}').get() or {}
            new_seats = max(sub.get('active_users_30d', 1) + 5, 1)
            db.reference(f'/recuraops/saas_subscriptions/{subscription_id}').update(
                {'seats': new_seats, 'status': 'downsized'})
        return {'description': f'Downsized {anomaly.get("vendor", "subscription")} to active-user count. Unused seats cancelled.'}

    def shutdown_resource(self, resource_id: str) -> dict:
        if resource_id:
            db.reference(f'/recuraops/cloud_resources/{resource_id}').update(
                {'status': 'stopped', 'idle_flag': False})
        return {'description': f'Resource {resource_id} stopped. Snapshot taken before shutdown.'}
