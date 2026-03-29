"""Decision Agent — GPT-4o powered anomaly analysis and ApprovalRequest creation."""
import os
import json
import logging
import uuid
from datetime import datetime, timezone
from firebase_admin import db
from app.agents import update_agent_status

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are RecuraOps Decision Agent — an enterprise cost intelligence AI.
Analyze the financial anomaly and return ONLY valid JSON with these exact fields:
{"severity":"critical|high|medium|low","recommended_action":"block_payment|cancel_licenses|shutdown_resource|notify_only","reasoning":"1-2 sentence plain English explanation","financial_impact_monthly":<INR number>,"financial_impact_annual":<INR number>,"requires_approval":true|false}
requires_approval is true if financial_impact_monthly > 10000."""


class DecisionAgent:
    name = 'decision_agent'

    def analyze(self, anomaly_id: str, anomaly: dict):
        update_agent_status(self.name, 'running')
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': json.dumps(anomaly, default=str)},
                ],
                response_format={'type': 'json_object'},
                max_tokens=400, temperature=0.3,
            )
            decision = json.loads(response.choices[0].message.content)
            db.reference(f'/recuraops/anomalies/{anomaly_id}').update({
                'severity': decision.get('severity', anomaly.get('severity', 'medium')),
                'ai_reasoning': decision.get('reasoning', ''),
                'financial_impact_monthly': decision.get('financial_impact_monthly', anomaly.get('financial_impact_monthly', 0)),
                'financial_impact_annual': decision.get('financial_impact_annual', anomaly.get('financial_impact_annual', 0)),
                'recommended_action': decision.get('recommended_action', anomaly.get('recommended_action', 'notify_only')),
            })
            if decision.get('requires_approval', True):
                apr_id = f'APR-{uuid.uuid4().hex[:6].upper()}'
                impact_m = decision.get('financial_impact_monthly', anomaly.get('financial_impact_monthly', 0))
                impact_a = decision.get('financial_impact_annual', anomaly.get('financial_impact_annual', 0))
                db.reference(f'/recuraops/approval_requests/{apr_id}').set({
                    'anomaly_id': anomaly_id,
                    'title': anomaly.get('title', 'Cost Anomaly Action Required'),
                    'requested_by': 'system_agent',
                    'requested_at': datetime.now(timezone.utc).isoformat(),
                    'action': decision.get('recommended_action', 'notify_only'),
                    'impact': f'Save ₹{impact_m:,.0f}/month (₹{impact_a:,.0f}/year)',
                    'status': 'pending',
                    'priority': decision.get('severity', 'medium'),
                })
            update_agent_status(self.name, 'idle')
        except Exception as e:
            update_agent_status(self.name, 'error')
            logger.error(f'DecisionAgent error for {anomaly_id}: {e}')
