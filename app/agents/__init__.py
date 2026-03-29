"""Agents package — shared in-memory status tracking."""
import threading
from datetime import datetime, timezone

agent_status = {
    'monitoring_agent':  {'status': 'idle', 'last_run': '2025-03-15T10:30:00Z', 'items_processed': 15, 'label': 'Monitoring'},
    'detection_agent':   {'status': 'idle', 'last_run': '2025-03-15T10:30:00Z', 'items_processed': 6,  'label': 'Detection'},
    'decision_agent':    {'status': 'idle', 'last_run': '2025-03-15T10:30:00Z', 'items_processed': 6,  'label': 'Decision'},
    'action_agent':      {'status': 'idle', 'last_run': '2025-03-15T09:30:00Z', 'items_processed': 2,  'label': 'Action'},
    'verification_agent':{'status': 'idle', 'last_run': '2025-03-15T09:32:00Z', 'items_processed': 2,  'label': 'Verification'},
}
_lock = threading.Lock()


def update_agent_status(agent_name: str, status: str, items_processed: int = None):
    with _lock:
        if agent_name in agent_status:
            agent_status[agent_name]['status'] = status
            agent_status[agent_name]['last_run'] = datetime.now(timezone.utc).isoformat()
            if items_processed is not None:
                agent_status[agent_name]['items_processed'] = items_processed
