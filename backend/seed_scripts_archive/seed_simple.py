"""
Simple seed script for minimum data to make dashboards work
"""
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

try:
    print("\n🚀 Adding Minimum Data for Dashboards...\n")

    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()

    if not users or not assets:
        print("❌ Run seed_data.py first!")
        exit(1)

    # Add audit logs
    print("📜 Adding 50 audit logs...")
    for i in range(50):
        log = models.AuditLog(
            user_id=random.choice(users).user_id,
            action=random.choice(["CREATE", "UPDATE", "DELETE", "VIEW", "APPROVE"]),
            entity_type=random.choice(["Asset", "ChangeRequest", "SLAMetric", "Policy", "Webhook"]),
            entity_id=random.randint(1, 10),
            ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
        )
        db.add(log)
    db.commit()
    print("  ✓ Created 50 audit logs")

    # Add compliance metrics time series
    print("📈 Adding 90 days of compliance metrics...")
    for days_ago in range(90, 0, -1):
        total = random.randint(45, 55)
        compliant = random.randint(38, min(52, total))
        metric = models.ComplianceMetric(
            metric_date=datetime.utcnow() - timedelta(days=days_ago),
            total_assets=total,
            compliant_assets=compliant,
            compliance_rate=int((compliant / total) * 100),
            missing_documentation=random.randint(0, 10),
            version_conflicts=random.randint(0, 5),
            pending_changes=random.randint(0, 8)
        )
        db.add(metric)
    db.commit()
    print("  ✓ Created 90 days of compliance metrics")

    print("\n✅ Basic data seeded! SLA dashboard will show 5 metrics, others will show empty states.\n")
    print("📝 Note: Some dashboards (API Keys, Webhooks, Events, Quality, Lineage)")
    print("   will show 'No data' until you create entries via the UI or fix the full seed script.\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
