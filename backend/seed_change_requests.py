"""
Seed script to create comprehensive change requests for assets
"""
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

try:
    print("\n📋 Generating Change Requests...\n")

    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()

    if not users or not assets:
        print("❌ Run seed_data.py and seed_large_dataset.py first!")
        exit(1)

    print(f"Found {len(users)} users and {len(assets)} assets\n")

    # Clear existing change requests
    db.query(models.ChangeRequest).delete()
    db.commit()
    print("  ✓ Cleared existing change requests\n")

    # Change request templates
    change_types = ["Modify", "Deploy", "Decommission", "Config"]
    risk_levels = ["Low", "Medium", "High", "Critical"]
    approval_statuses = ["Pending", "Approved", "Rejected"]
    statuses = ["Submitted", "InProgress", "Completed", "RolledBack"]

    # Change request titles by type
    title_templates = {
        "Modify": [
            "Update {} to latest version",
            "Modify {} configuration for performance optimization",
            "Change {} database schema",
            "Update {} security settings",
            "Modify {} integration endpoints",
        ],
        "Deploy": [
            "Deploy {} to production environment",
            "Deploy new version of {}",
            "Deploy {} hotfix release",
            "Deploy {} feature update",
            "Deploy {} to UAT for testing",
        ],
        "Decommission": [
            "Decommission legacy {} system",
            "Retire outdated {} infrastructure",
            "Decommission {} and migrate to new platform",
            "Phase out {} system",
            "Sunset {} application",
        ],
        "Config": [
            "Configure {} backup schedule",
            "Update {} monitoring alerts",
            "Configure {} load balancing",
            "Update {} SSL certificates",
            "Configure {} disaster recovery",
        ]
    }

    # Descriptions
    description_templates = {
        "Modify": [
            "This change request is to modify the system configuration to improve performance and reliability. The changes include updating database connection pools, optimizing query execution, and enhancing caching mechanisms.",
            "Update system to address security vulnerabilities identified in the latest security audit. This includes patching known CVEs and implementing enhanced authentication mechanisms.",
            "Modify integration endpoints to align with new API specifications from vendor. This change will ensure compatibility and enable new features.",
        ],
        "Deploy": [
            "Deploy the latest version which includes bug fixes, performance improvements, and new features requested by business stakeholders. This deployment has been thoroughly tested in QA environment.",
            "Deploy critical hotfix to address production issues reported by end users. The fix has been validated in development and QA environments.",
            "Deploy new feature release that enables advanced analytics capabilities and improves user experience based on feedback.",
        ],
        "Decommission": [
            "Decommission this legacy system as part of the digital transformation initiative. All users have been migrated to the new platform and data has been archived.",
            "Retire this outdated infrastructure to reduce operational costs and technical debt. Replacement system is already operational.",
            "Phase out this system as it has reached end-of-life and vendor support has been discontinued. Migration plan has been executed successfully.",
        ],
        "Config": [
            "Configure system settings to align with updated compliance requirements and security policies. This includes enabling audit logging and encryption at rest.",
            "Update configuration to support increased load capacity and improved failover capabilities. This change will enhance system resilience.",
            "Configure new backup and disaster recovery procedures to meet RTO and RPO targets defined in the business continuity plan.",
        ]
    }

    # Impact assessments
    impact_templates = [
        "High impact: System will require 30-minute maintenance window. All users will be temporarily unable to access the system during deployment.",
        "Medium impact: Configuration changes will be applied during off-peak hours. Some features may be temporarily unavailable.",
        "Low impact: Changes will be deployed using blue-green deployment strategy. No user impact expected.",
        "Critical impact: This change affects core business operations. Extensive testing and rollback plan are required.",
        "Low impact: Internal system only, no end-user facing changes. Can be deployed during business hours.",
        "Medium impact: Database schema changes require brief read-only mode. Estimated downtime: 10 minutes.",
    ]

    # Rollback plans
    rollback_templates = [
        "Rollback procedure: 1) Stop new version, 2) Start previous version, 3) Restore database from backup if needed, 4) Verify system functionality. Estimated rollback time: 15 minutes.",
        "Automated rollback using deployment scripts. Previous version artifacts are retained in production for 48 hours. Rollback can be executed within 5 minutes.",
        "Database rollback script prepared and tested. Configuration changes can be reverted using version control. Rollback SOP documented in wiki.",
        "Blue-green deployment strategy allows instant rollback by redirecting traffic to previous version. No data migration required for rollback.",
        "Rollback plan: Restore from snapshot created before deployment. Re-apply previous configuration files. Restart services in correct order.",
    ]

    change_requests = []
    cr_count = 0

    # Create 50-80 change requests
    num_requests = random.randint(50, 80)

    for i in range(num_requests):
        # Select random asset
        asset = random.choice(assets)

        # Select random change type
        change_type = random.choice(change_types)

        # Generate title
        title = random.choice(title_templates[change_type]).format(asset.asset_name)

        # Generate description
        description = random.choice(description_templates[change_type])

        # Risk level - weighted towards Low/Medium
        risk_weights = [40, 35, 20, 5]  # Low, Medium, High, Critical
        risk_level = random.choices(risk_levels, weights=risk_weights)[0]

        # Impact assessment
        impact_assessment = random.choice(impact_templates)

        # Rollback plan
        rollback_plan = random.choice(rollback_templates)

        # Requester
        requested_by = random.choice(users).user_id

        # Request date (within last 90 days)
        requested_at = datetime.utcnow() - timedelta(
            days=random.randint(1, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Approval status - weighted towards Approved
        approval_weights = [20, 65, 15]  # Pending, Approved, Rejected
        approval_status = random.choices(approval_statuses, weights=approval_weights)[0]

        # Approver and approval date (if approved or rejected)
        approver_id = None
        approved_at = None
        approval_comments = None

        if approval_status in ["Approved", "Rejected"]:
            approver_id = random.choice(users).user_id
            approved_at = requested_at + timedelta(
                days=random.randint(1, 7),
                hours=random.randint(0, 23)
            )

            if approval_status == "Approved":
                approval_comments = random.choice([
                    "Approved after architecture review. Proceed with implementation during next maintenance window.",
                    "Change approved. Ensure all stakeholders are notified before deployment.",
                    "Approved with recommendation to monitor system closely post-deployment.",
                    "Change request approved. Coordinate with infrastructure team for implementation.",
                ])
            else:
                approval_comments = random.choice([
                    "Rejected due to insufficient testing. Please provide additional test results and resubmit.",
                    "Rejected - conflicts with upcoming infrastructure upgrade. Defer until next quarter.",
                    "Risk assessment insufficient. Please provide detailed impact analysis and resubmit.",
                    "Rejected - alternative solution recommended. Please review with architecture team.",
                ])

        # Status - based on approval status
        if approval_status == "Pending":
            status = "Submitted"
        elif approval_status == "Rejected":
            status = "Submitted"
        else:  # Approved
            status_weights = [10, 40, 50]  # InProgress, Completed, Submitted (waiting)
            status = random.choices(["InProgress", "Completed", "Submitted"], weights=status_weights)[0]

        # Implementation date (if completed)
        implementation_date = None
        if status == "Completed":
            implementation_date = approved_at + timedelta(
                days=random.randint(1, 14),
                hours=random.randint(0, 23)
            )

        # Release version (for deploy changes)
        release_version = None
        if change_type == "Deploy" and approval_status == "Approved":
            major = random.randint(1, 5)
            minor = random.randint(0, 15)
            patch = random.randint(0, 30)
            release_version = f"{major}.{minor}.{patch}"

        # Create change request
        change_request = models.ChangeRequest(
            title=title,
            description=description,
            asset_id=asset.asset_id,
            change_type=change_type,
            risk_level=risk_level,
            impact_assessment=impact_assessment,
            rollback_plan=rollback_plan,
            requested_by=requested_by,
            requested_at=requested_at,
            approval_status=approval_status,
            approver_id=approver_id,
            approved_at=approved_at,
            approval_comments=approval_comments,
            implementation_date=implementation_date,
            status=status,
            release_version=release_version,
        )

        db.add(change_request)
        change_requests.append(change_request)
        cr_count += 1

        if cr_count % 20 == 0:
            print(f"  ✓ Created {cr_count} change requests...")

    db.commit()
    print(f"\n  ✓ Created total {cr_count} change requests")

    # Summary
    from sqlalchemy import func

    print(f"\n{'='*60}")
    print(f"✅ Change Requests Created Successfully!")
    print(f"{'='*60}")
    print(f"📊 Total Change Requests: {cr_count}")

    # Count by change type
    by_type = (
        db.query(models.ChangeRequest.change_type, func.count(models.ChangeRequest.change_id))
        .group_by(models.ChangeRequest.change_type)
        .all()
    )

    print(f"\n📋 By Change Type:")
    for change_type, count in sorted(by_type, key=lambda x: x[1], reverse=True):
        print(f"   - {change_type}: {count} requests")

    # Count by risk level
    by_risk = (
        db.query(models.ChangeRequest.risk_level, func.count(models.ChangeRequest.change_id))
        .group_by(models.ChangeRequest.risk_level)
        .all()
    )

    print(f"\n⚠️  By Risk Level:")
    for risk, count in sorted(by_risk, key=lambda x: x[1], reverse=True):
        print(f"   - {risk}: {count} requests")

    # Count by approval status
    by_approval = (
        db.query(models.ChangeRequest.approval_status, func.count(models.ChangeRequest.change_id))
        .group_by(models.ChangeRequest.approval_status)
        .all()
    )

    print(f"\n✅ By Approval Status:")
    for approval, count in sorted(by_approval, key=lambda x: x[1], reverse=True):
        print(f"   - {approval}: {count} requests")

    # Count by status
    by_status = (
        db.query(models.ChangeRequest.status, func.count(models.ChangeRequest.change_id))
        .group_by(models.ChangeRequest.status)
        .all()
    )

    print(f"\n🔄 By Status:")
    for status, count in sorted(by_status, key=lambda x: x[1], reverse=True):
        print(f"   - {status}: {count} requests")

    print(f"{'='*60}\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
