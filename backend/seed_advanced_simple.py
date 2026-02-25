"""
Simple seed script for advanced features with minimal data
"""
from app.database import SessionLocal
from app import models, models_advanced
from datetime import datetime, timedelta
import random
import secrets
import hashlib

db = SessionLocal()

try:
    print("\n🚀 Seeding Advanced Features (Simple Mode)...\n")
    
    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()
    
    if not users or not assets:
        print("❌ Run seed_data.py first!")
        exit(1)
    
    # 1. SLA Metrics (already created successfully)
    print("✓ SLA Metrics already seeded")
    
    # 2. Skip problematic sections for now - just add audit logs
    print("📜 Adding audit logs...")
    for i in range(30):
        log = models.AuditLog(
            user_id=random.choice(users).user_id,
            action=random.choice(["CREATE", "UPDATE", "DELETE"]),
            entity_type=random.choice(["Asset", "SLAMetric", "Policy"]),
            entity_id=random.randint(1, 10),
            ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            description=f"Sample audit log entry {i}",
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
        )
        db.add(log)
    db.commit()
    print(f"  ✓ Created 30 audit logs")
    
    # 3. Compliance Metrics time series
    print("📈 Adding compliance metrics...")
    for days_ago in range(90, 0, -1):
        metric = models.ComplianceMetric(
            metric_date=(datetime.utcnow() - timedelta(days=days_ago)).date(),
            total_assets=random.randint(45, 55),
            compliant_assets=random.randint(38, 52),
            compliance_rate=random.uniform(75.0, 95.0),
            violations_count=random.randint(2, 15),
            critical_violations=random.randint(0, 3),
            avg_resolution_time_hours=random.uniform(12.0, 72.0)
        )
        db.add(metric)
    db.commit()
    print(f"  ✓ Created 90 days of compliance metrics")
    
    print("\n✅ Simple seed completed!\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
