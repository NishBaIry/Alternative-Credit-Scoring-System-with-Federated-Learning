# audit_service.py
# Service for logging and auditing system activities.
# Functions:
# - log_event(user_id, action, details): records an audit event
# - get_audit_trail(bank_id, filters): retrieves audit logs for compliance
# - log_model_training(bank_id, metrics): logs training events
# - log_score_access(user_id, customer_id): logs when scores are viewed
# Important for regulatory compliance and demonstrating responsible AI practices.

from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class AuditService:
    """Service for audit logging and compliance."""
    
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
        self.audit_log_path = Path(f"app/data/{bank_id}/audit_log.jsonl")
    
    def log_event(
        self, 
        user_id: str, 
        action: str, 
        details: Optional[Dict] = None
    ) -> None:
        """
        Log an audit event.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "bank_id": self.bank_id,
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
        
        # Append to log file
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def log_model_training(
        self, 
        user_id: str, 
        metrics: Dict
    ) -> None:
        """
        Log a model training event.
        """
        self.log_event(
            user_id=user_id,
            action="model_training",
            details={
                "metrics": metrics,
                "model_version": "1.0"
            }
        )
    
    def log_score_access(
        self, 
        user_id: str, 
        customer_id: str,
        access_type: str = "view"
    ) -> None:
        """
        Log when a score is accessed.
        """
        self.log_event(
            user_id=user_id,
            action=f"score_{access_type}",
            details={"customer_id": customer_id}
        )
    
    def log_fl_update(
        self, 
        user_id: str, 
        round_number: int,
        privacy_budget_used: float
    ) -> None:
        """
        Log a federated learning update.
        """
        self.log_event(
            user_id=user_id,
            action="fl_update_sent",
            details={
                "round": round_number,
                "privacy_budget_used": privacy_budget_used
            }
        )
    
    def get_audit_trail(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit logs with filters.
        """
        if not self.audit_log_path.exists():
            return []
        
        events = []
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                event = json.loads(line)
                
                # Apply filters
                if action_filter and event['action'] != action_filter:
                    continue
                
                if start_date:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    if event_time < start_date:
                        continue
                
                if end_date:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    if event_time > end_date:
                        continue
                
                events.append(event)
                
                if len(events) >= limit:
                    break
        
        return events
    
    def get_stats(self) -> Dict:
        """
        Get audit statistics.
        """
        events = self.get_audit_trail(limit=10000)
        
        action_counts = {}
        for event in events:
            action = event['action']
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_events": len(events),
            "action_breakdown": action_counts,
            "bank_id": self.bank_id
        }

def get_audit_service(bank_id: str) -> AuditService:
    """Factory function to get audit service for a bank."""
    return AuditService(bank_id)
