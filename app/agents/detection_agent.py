"""Detection Agent — rule-based anomaly detection."""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from firebase_admin import db
from app.agents import update_agent_status

logger = logging.getLogger(__name__)


class DetectionAgent:
    name = 'detection_agent'

    def run(self, data: dict):
        update_agent_status(self.name, 'running')
        try:
            detected = (self.detect_duplicates(data.get('vendor_invoices', {})) +
                        self.detect_inactive_subscriptions(data.get('saas_subscriptions', {})) +
                        self.detect_idle_resources(data.get('cloud_resources', {})))
            existing = db.reference('/recuraops/anomalies').get() or {}
            existing_titles = {v.get('title') for v in existing.values()}
            new_count = 0
            for anomaly in detected:
                if anomaly['title'] not in existing_titles:
                    ano_id = f'ANO-{uuid.uuid4().hex[:6].upper()}'
                    db.reference(f'/recuraops/anomalies/{ano_id}').set(anomaly)
                    from app.agents.decision_agent import DecisionAgent
                    DecisionAgent().analyze(ano_id, anomaly)
                    new_count += 1
            update_agent_status(self.name, 'idle', items_processed=len(detected))
        except Exception as e:
            update_agent_status(self.name, 'error')
            logger.error(f'DetectionAgent error: {e}')

    def detect_duplicates(self, invoices: dict) -> list:
        seen, anomalies = {}, []
        for inv_id, inv in invoices.items():
            key = (inv.get('vendor'), inv.get('amount'), inv.get('invoice_ref'))
            if key in seen and inv.get('status') == 'pending':
                anomalies.append({
                    'type': 'duplicate_invoice', 'severity': 'high',
                    'title': f'Duplicate Invoice — {inv.get("vendor", "Unknown")}',
                    'description': f'Invoice {inv.get("invoice_ref")} from {inv.get("vendor")} appears to be a duplicate.',
                    'affected_entity': inv_id, 'vendor': inv.get('vendor'),
                    'financial_impact_monthly': inv.get('amount', 0),
                    'financial_impact_annual': inv.get('amount', 0) * 12,
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'pending_approval', 'recommended_action': 'block_payment',
                    'agent': self.name,
                })
            else:
                seen[key] = inv_id
        return anomalies

    def detect_inactive_subscriptions(self, saas: dict) -> list:
        anomalies = []
        for sub_id, sub in saas.items():
            util = sub.get('utilization_pct', 100)
            if util < 15.0:
                anomalies.append({
                    'type': 'inactive_subscription',
                    'severity': 'high' if util < 10 else 'medium',
                    'title': f'{sub.get("tool")} — {100 - util:.0f}% Seats Unused',
                    'description': (f'{sub.get("seats")} {sub.get("tool")} {sub.get("plan")} seats purchased. '
                                    f'Only {sub.get("active_users_30d")} active in last 30 days ({util}% utilization).'),
                    'affected_entity': sub_id, 'vendor': sub.get('tool'),
                    'financial_impact_monthly': int(sub.get('monthly_cost', 0) * 0.8),
                    'financial_impact_annual': int(sub.get('monthly_cost', 0) * 0.8 * 12),
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'pending_approval', 'recommended_action': 'cancel_licenses',
                    'agent': self.name,
                })
        return anomalies

    def detect_idle_resources(self, cloud: dict) -> list:
        anomalies = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        for res_id, res in cloud.items():
            cpu = res.get('cpu_avg_7d', 100)
            try:
                last_active = datetime.fromisoformat(res.get('last_active', '').replace('Z', '+00:00'))
            except Exception:
                last_active = datetime.now(timezone.utc)
            if cpu < 5.0 and last_active < cutoff:
                anomalies.append({
                    'type': 'idle_cloud_resource', 'severity': 'high',
                    'title': f'Idle {res.get("resource_type")} — {res.get("region")}',
                    'description': (f'{res.get("resource_type")} {res.get("instance_id")} '
                                    f'has averaged {cpu}% CPU over 7 days. Recommend shutdown.'),
                    'affected_entity': res_id, 'vendor': res.get('provider'),
                    'financial_impact_monthly': res.get('monthly_cost', 0),
                    'financial_impact_annual': res.get('monthly_cost', 0) * 12,
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'pending_approval', 'recommended_action': 'shutdown_resource',
                    'agent': self.name,
                })
        return anomalies
