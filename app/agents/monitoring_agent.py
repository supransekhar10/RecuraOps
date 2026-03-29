"""Monitoring Agent — runs every 5 minutes, fetches Firebase data, triggers DetectionAgent."""
import logging
from datetime import datetime, timezone
from firebase_admin import db
from app.agents import update_agent_status

logger = logging.getLogger(__name__)


class MonitoringAgent:
    name = 'monitoring_agent'

    def run(self):
        update_agent_status(self.name, 'running')
        try:
            data = {
                'vendor_invoices': db.reference('/recuraops/vendor_invoices').get() or {},
                'saas_subscriptions': db.reference('/recuraops/saas_subscriptions').get() or {},
                'cloud_resources': db.reference('/recuraops/cloud_resources').get() or {},
            }
            total = sum(len(v) for v in data.values())
            ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            db.reference(f'/recuraops/raw_snapshots/{ts}').set({
                'captured_at': datetime.now(timezone.utc).isoformat(),
                'invoice_count': len(data['vendor_invoices']),
                'subscription_count': len(data['saas_subscriptions']),
                'cloud_resource_count': len(data['cloud_resources']),
            })
            from app.agents.detection_agent import DetectionAgent
            DetectionAgent().run(data)
            update_agent_status(self.name, 'idle', items_processed=total)
        except Exception as e:
            update_agent_status(self.name, 'error')
            logger.error(f'MonitoringAgent error: {e}')
