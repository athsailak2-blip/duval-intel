#!/usr/bin/env python3
"""
PRR Submission Tracker Module
Tracks Public Records Request submissions, status, and follow-ups for data sources
that require PRR access (e.g., Code Enforcement, detailed court records).
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

PRR_TRACKER_FILE = os.environ.get('PRR_TRACKER_FILE', 'data/prr_submissions.json')

class PRRSubmissionTracker:
    """Track PRR submissions and manage follow-up workflow."""
    
    def __init__(self, tracker_file: str = None):
        self.tracker_file = tracker_file or PRR_TRACKER_FILE
        self.submissions = self._load_submissions()
    
    def _load_submissions(self) -> List[Dict]:
        """Load existing PRR submissions from file."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                    return data.get('submissions', [])
            except Exception as e:
                print(f"Error loading PRR tracker: {e}")
        return []
    
    def _save_submissions(self):
        """Save submissions to file."""
        os.makedirs(os.path.dirname(self.tracker_file) or '.', exist_ok=True)
        with open(self.tracker_file, 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'total_submissions': len(self.submissions),
                'submissions': self.submissions
            }, f, indent=2)
    
    def submit_prr(self, source_id: str, request_type: str, 
                   description: str, submission_method: str,
                   contact_info: Dict, estimated_cost: float = 0.0,
                   requested_fields: List[str] = None,
                   date_range: Dict = None) -> Dict:
        """Record a new PRR submission."""
        submission_id = f"PRR-{datetime.now().strftime('%Y%m%d')}-{len(self.submissions)+1:03d}"
        
        submission = {
            'submission_id': submission_id,
            'source_id': source_id,
            'request_type': request_type,
            'description': description,
            'submission_method': submission_method,
            'contact_info': contact_info,
            'estimated_cost': estimated_cost,
            'requested_fields': requested_fields or [],
            'date_range': date_range or {'start': '', 'end': ''},
            'status': 'submitted',
            'submitted_at': datetime.now().isoformat(),
            'acknowledged_at': None,
            'completed_at': None,
            'follow_up_dates': [],
            'notes': [],
            'tracking_number': None,
            'cost_actual': None,
            'data_received': False,
            'data_file_path': None,
            'records_count': 0
        }
        
        # Calculate follow-up dates (5 and 10 business days)
        submitted = datetime.now()
        follow_up_5 = submitted + timedelta(days=7)
        follow_up_10 = submitted + timedelta(days=14)
        
        submission['follow_up_dates'] = [
            {'date': follow_up_5.isoformat(), 'type': 'status_check', 'completed': False},
            {'date': follow_up_10.isoformat(), 'type': 'escalation', 'completed': False}
        ]
        
        self.submissions.append(submission)
        self._save_submissions()
        
        print(f"PRR submitted: {submission_id} for {source_id}")
        return submission
    
    def update_status(self, submission_id: str, status: str,
                      tracking_number: str = None, notes: str = None) -> Dict:
        """Update the status of a PRR submission."""
        for sub in self.submissions:
            if sub['submission_id'] == submission_id:
                sub['status'] = status
                if tracking_number:
                    sub['tracking_number'] = tracking_number
                if notes:
                    sub['notes'].append({
                        'date': datetime.now().isoformat(),
                        'text': notes
                    })
                
                if status == 'acknowledged':
                    sub['acknowledged_at'] = datetime.now().isoformat()
                elif status in ['completed', 'fulfilled', 'partial']:
                    sub['completed_at'] = datetime.now().isoformat()
                    if status == 'fulfilled':
                        sub['data_received'] = True
                
                self._save_submissions()
                print(f"Updated {submission_id}: status = {status}")
                return sub
        
        print(f"Submission {submission_id} not found")
        return None
    
    def record_data_received(self, submission_id: str, 
                            file_path: str, records_count: int,
                            actual_cost: float = None) -> Dict:
        """Record that data was received for a PRR."""
        for sub in self.submissions:
            if sub['submission_id'] == submission_id:
                sub['data_received'] = True
                sub['data_file_path'] = file_path
                sub['records_count'] = records_count
                sub['status'] = 'data_received'
                if actual_cost is not None:
                    sub['cost_actual'] = actual_cost
                sub['notes'].append({
                    'date': datetime.now().isoformat(),
                    'text': f'Received {records_count} records'
                })
                self._save_submissions()
                print(f"Data recorded for {submission_id}: {records_count} records")
                return sub
        return None
    
    def get_pending_follow_ups(self) -> List[Dict]:
        """Get submissions that need follow-up action."""
        now = datetime.now()
        pending = []
        
        for sub in self.submissions:
            if sub['status'] in ['completed', 'fulfilled', 'data_received']:
                continue
            
            for fu in sub.get('follow_up_dates', []):
                if not fu['completed'] and datetime.fromisoformat(fu['date']) <= now:
                    pending.append({
                        'submission_id': sub['submission_id'],
                        'source_id': sub['source_id'],
                        'status': sub['status'],
                        'follow_up_type': fu['type'],
                        'follow_up_date': fu['date'],
                        'days_since_submission': (now - datetime.fromisoformat(sub['submitted_at'])).days
                    })
        
        return pending
    
    def get_submissions_by_source(self, source_id: str) -> List[Dict]:
        """Get all submissions for a specific source."""
        return [s for s in self.submissions if s['source_id'] == source_id]
    
    def get_overdue_submissions(self, days_threshold: int = 14) -> List[Dict]:
        """Get submissions that are overdue for response."""
        now = datetime.now()
        overdue = []
        
        for sub in self.submissions:
            if sub['status'] in ['completed', 'fulfilled', 'data_received']:
                continue
            
            submitted = datetime.fromisoformat(sub['submitted_at'])
            days_elapsed = (now - submitted).days
            
            if days_elapsed > days_threshold:
                overdue.append({
                    'submission_id': sub['submission_id'],
                    'source_id': sub['source_id'],
                    'status': sub['status'],
                    'days_elapsed': days_elapsed,
                    'submitted_at': sub['submitted_at']
                })
        
        return overdue
    
    def generate_report(self) -> Dict:
        """Generate summary report of all PRR activity."""
        total = len(self.submissions)
        by_status = {}
        by_source = {}
        
        for sub in self.submissions:
            status = sub['status']
            by_status[status] = by_status.get(status, 0) + 1
            
            source = sub['source_id']
            if source not in by_source:
                by_source[source] = {'total': 0, 'completed': 0, 'pending': 0}
            by_source[source]['total'] += 1
            if sub['status'] in ['completed', 'fulfilled', 'data_received']:
                by_source[source]['completed'] += 1
            else:
                by_source[source]['pending'] += 1
        
        total_records = sum(s.get('records_count', 0) for s in self.submissions)
        total_cost = sum(s.get('cost_actual', 0) or 0 for s in self.submissions)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'total_submissions': total,
            'by_status': by_status,
            'by_source': by_source,
            'total_records_received': total_records,
            'total_cost': total_cost,
            'pending_follow_ups': len(self.get_pending_follow_ups()),
            'overdue_submissions': len(self.get_overdue_submissions())
        }

# Pre-configured PRR templates for Duval County sources
PRR_TEMPLATES = {
    'code_enforcement': {
        'source_id': 'duval_code_enforcement',
        'request_type': 'Code Enforcement Cases',
        'description': 'Request for all open and recently closed code enforcement cases including violation type, property address, RE number, case status, open/close dates, lien amounts, and lien recording dates.',
        'submission_method': 'online_portal',
        'requested_fields': [
            'case_id', 'property_address', 're_number', 'violation_type',
            'case_status', 'open_date', 'close_date', 'lien_amount',
            'lien_recording_date', 'property_owner'
        ],
        'portal_url': 'https://jacksonvillefl.govqa.us/WEBAPP/_rs/supporthome.aspx',
        'email': 'myjax@custhelp.com',
        'mail_address': 'Jacksonville Municipal Code Compliance Division, Attn: Public Records Coordinator, 214 North Hogan Street, 7th Floor, Jacksonville, FL 32202',
        'phone': '(904) 630-2489'
    }
}

def create_prr_from_template(template_name: str, contact_info: Dict,
                             date_range: Dict = None, estimated_cost: float = 0.0) -> Dict:
    """Create a PRR submission from a pre-configured template."""
    template = PRR_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")
    
    tracker = PRRSubmissionTracker()
    return tracker.submit_prr(
        source_id=template['source_id'],
        request_type=template['request_type'],
        description=template['description'],
        submission_method=template['submission_method'],
        contact_info=contact_info,
        estimated_cost=estimated_cost,
        requested_fields=template['requested_fields'],
        date_range=date_range
    )

if __name__ == '__main__':
    # Example usage
    tracker = PRRSubmissionTracker()
    
    # Create a sample PRR
    contact = {
        'name': 'Data Collection Team',
        'organization': 'Duval Intel Project',
        'email': 'data@example.com',
        'phone': '555-0100'
    }
    
    submission = create_prr_from_template(
        'code_enforcement',
        contact,
        date_range={'start': '2024-01-01', 'end': '2026-06-01'},
        estimated_cost=25.0
    )
    
    print("\nPRR Report:")
    print(json.dumps(tracker.generate_report(), indent=2))
