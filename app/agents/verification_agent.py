"""Verification Agent — confirms actions completed, updates KPI summary."""
import logging
from datetime import datetime, timezone
from firebase_admin import db
from app.agents import update_agent_status

logger = logging.getLogger(__name__)


class VerificationAgent:
    name = 'verification_agent'

    def verify(self, action_log_id: str):
        update_agent_status(self.name, 'running')
        try:
            act = db.reference(f'/recuraops/action_log/{action_log_id}').get()
            if not act:
                return
            action_type = act.get('action', '')
            anomaly = db.reference(f'/recuraops/anomalies/{act.get("anomaly_id", "")}').get() or {}
            affected = anomaly.get('affected_entity', '')
            verified = False
            if action_type == 'block_payment' and affected:
                inv = db.reference(f'/recuraops/vendor_invoices/{affected}').get() or {}
                verified = inv.get('status') == 'blocked'
            elif action_type == 'cancel_licenses' and affected:
                sub = db.reference(f'/recuraops/saas_subscriptions/{affected}').get() or {}
                verified = sub.get('status') == 'downsized'
            elif action_type == 'shutdown_resource' and affected:
                res = db.reference(f'/recuraops/cloud_resources/{affected}').get() or {}
                verified = res.get('status') == 'stopped'
            else:
                verified = True
            db.reference(f'/recuraops/action_log/{action_log_id}').update({
                'verification_status': 'verified' if verified else 'failed',
                'verified_at': datetime.now(timezone.utc).isoformat(),
            })
            self.update_kpi_summary()
            update_agent_status(self.name, 'idle')
        except Exception as e:
            update_agent_status(self.name, 'error')
            logger.error(f'VerificationAgent error: {e}')

    def update_kpi_summary(self):
        try:
            all_anomalies = db.reference('/recuraops/anomalies').get() or {}
            action_log = db.reference('/recuraops/action_log').get() or {}
            approval_requests = db.reference('/recuraops/approval_requests').get() or {}
            db.reference('/recuraops/kpi_summary').update({
                'total_savings_realized_annual': sum(
                    a.get('savings_realized_annual', 0) for a in action_log.values() if a.get('status') == 'completed'),
                'total_savings_potential_annual': sum(
                    a.get('financial_impact_annual', 0) for a in all_anomalies.values()
                    if a.get('status') == 'pending_approval'),
                'active_issues': sum(1 for a in all_anomalies.values()
                                     if a.get('status') in ('pending_approval', 'detected')),
                'pending_approvals': sum(1 for a in approval_requests.values() if a.get('status') == 'pending'),
                'actions_executed': sum(1 for a in action_log.values() if a.get('status') == 'completed'),
                'last_scan': datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.error(f'VerificationAgent KPI update error: {e}')
