#!/usr/bin/env python3
"""Seed missing data for Change Requests, Compliance Violations, and Audit Logs"""

import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def seed_missing_data():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("  🚀 SEEDING MISSING DATA FOR DASHBOARDS")
        print("=" * 70)
        print()

        # Get existing counts
        change_requests_count = db.query(models.ChangeRequest).count()
        compliance_violations_count = db.query(models.ComplianceViolation).count()
        audit_logs_count = db.query(models.AuditLog).count()

        print(f"Current counts:")
        print(f"  - Change Requests: {change_requests_count}")
        print(f"  - Compliance Violations: {compliance_violations_count}")
        print(f"  - Audit Logs: {audit_logs_count}")
        print()

        # Seed Change Requests
        if change_requests_count < 20:
            print(f"Adding Change Requests (target: 20)...")
            change_requests = []

            for i in range(2, 21):  # Starting from 2 since 1 exists
                created_days_ago = random.randint(0, 60)
                approval_status = random.choice(['Pending', 'Approved', 'Rejected'])
                status = random.choice(['Submitted', 'InProgress', 'Completed', 'RolledBack'])
                risk_level = random.choice(['Low', 'Medium', 'High', 'Critical'])

                change_request = models.ChangeRequest(
                    title=f"CR-{i:03d}: {random.choice(['Update configuration', 'Modify schema', 'Performance tuning', 'Security patch', 'Feature enhancement'])}",
                    description=f"Change request {i}: Required to {random.choice(['improve performance', 'fix security issue', 'meet compliance', 'add new feature', 'reduce costs'])}. {risk_level} impact on {random.choice(['data quality', 'system performance', 'user experience', 'security posture'])}.",
                    asset_id=random.randint(1, 5),
                    requested_by=random.randint(1, 4),
                    change_type=random.choice(['Modify', 'Deploy', 'Decommission', 'Config']),
                    impact_assessment=f"{risk_level} impact on {random.choice(['data quality', 'system performance', 'user experience', 'security posture'])}",
                    rollback_plan=f"Restore from backup taken at {(datetime.utcnow() - timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%d %H:%M')}",
                    status=status,
                    risk_level=risk_level,
                    approval_status=approval_status,
                    approver_id=random.randint(1, 3) if approval_status in ['Approved', 'Rejected'] else None,
                    approved_at=datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago)) if approval_status in ['Approved', 'Rejected'] else None,
                    approval_comments=f"{random.choice(['Approved for deployment', 'Rejected due to risk', 'Requires additional testing'])}" if approval_status in ['Approved', 'Rejected'] else None,
                    implementation_date=datetime.utcnow() - timedelta(days=random.randint(0, 5)) if status == 'Completed' else None,
                    requested_at=datetime.utcnow() - timedelta(days=created_days_ago),
                    release_version=f"v{random.randint(1, 5)}.{random.randint(0, 10)}" if status in ['InProgress', 'Completed'] else None
                )
                change_requests.append(change_request)

            db.bulk_save_objects(change_requests)
            db.commit()
            print(f"✓ Created {len(change_requests)} change requests")
        else:
            print(f"✓ Change Requests already populated ({change_requests_count} records)")

        # Seed Compliance Violations
        if compliance_violations_count < 25:
            print(f"Adding Compliance Violations (target: 25)...")
            violations = []

            for i in range(2, 26):  # Starting from 2 since 1 exists
                detected_days_ago = random.randint(0, 90)
                has_resolution = random.choice([True, False, False])  # 33% resolved
                severity = random.choice(['Low', 'Medium', 'High'])  # Note: 'Critical' not in CHECK constraint

                violation_descriptions = [
                    'Asset name does not follow standard naming convention',
                    'Required documentation is missing or outdated',
                    'Encryption not enabled for sensitive data',
                    'Data classification labels are incorrect',
                    'SLA response time exceeded threshold',
                    'Unauthorized access detected',
                    'Data retention period not configured'
                ]

                resolution_actions = ['updating configuration', 'modifying asset properties', 'applying security patch', 'updating documentation']

                violation = models.ComplianceViolation(
                    asset_id=random.randint(1, 5),
                    violation_type=random.choice([
                        'Naming Convention Violation',
                        'Missing Documentation',
                        'Security Policy Violation',
                        'Data Classification Issue',
                        'SLA Breach',
                        'Access Control Violation',
                        'Retention Policy Violation'
                    ]),
                    severity=severity,
                    description=f"Violation #{i}: {random.choice(violation_descriptions)}",
                    detected_at=datetime.utcnow() - timedelta(days=detected_days_ago),
                    resolved_at=datetime.utcnow() - timedelta(days=random.randint(0, detected_days_ago)) if has_resolution else None,
                    resolved_by=random.randint(1, 4) if has_resolution else None,
                    resolution_notes=f"Fixed by {random.choice(resolution_actions)}" if has_resolution else None
                )
                violations.append(violation)

            db.bulk_save_objects(violations)
            db.commit()
            print(f"✓ Created {len(violations)} compliance violations")
        else:
            print(f"✓ Compliance Violations already populated ({compliance_violations_count} records)")

        # Seed Audit Logs
        if audit_logs_count < 100:
            print(f"Adding Audit Logs (target: 100)...")
            audit_logs = []

            for i in range(1, 101):
                logged_days_ago = random.randint(0, 30)
                action = random.choice([
                    'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'LOGIN', 'LOGOUT',
                    'APPROVE', 'REJECT', 'EXPORT', 'IMPORT', 'CONFIGURE'
                ])
                entity_type = random.choice(['Asset', 'User', 'Domain', 'Vendor', 'ChangeRequest', 'Policy'])

                old_val = random.choice(["Active", "Draft", "Pending", "v1.0", "admin"])
                new_val = random.choice(["Active", "Completed", "Approved", "v2.0", "editor"])

                audit_log = models.AuditLog(
                    user_id=random.randint(1, 4),
                    action=action,
                    entity_type=entity_type,
                    entity_id=random.randint(1, 10),
                    old_value=old_val if action == 'UPDATE' else None,
                    new_value=new_val if action in ['CREATE', 'UPDATE'] else None,
                    ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    user_agent=random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
                        'Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0'
                    ]),
                    timestamp=datetime.utcnow() - timedelta(days=logged_days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                )
                audit_logs.append(audit_log)

            db.bulk_save_objects(audit_logs)
            db.commit()
            print(f"✓ Created {len(audit_logs)} audit logs")
        else:
            print(f"✓ Audit Logs already populated ({audit_logs_count} records)")

        print()
        print("=" * 70)
        print("  ✓ Successfully seeded missing dashboard data!")
        print("=" * 70)

        # Print final counts
        final_change_requests = db.query(models.ChangeRequest).count()
        final_violations = db.query(models.ComplianceViolation).count()
        final_audit_logs = db.query(models.AuditLog).count()

        print()
        print("Final counts:")
        print(f"  - Change Requests: {final_change_requests}")
        print(f"  - Compliance Violations: {final_violations}")
        print(f"  - Audit Logs: {final_audit_logs}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding missing data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_missing_data()
