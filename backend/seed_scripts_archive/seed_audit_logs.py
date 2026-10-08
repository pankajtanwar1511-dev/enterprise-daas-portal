"""
Seed script to create comprehensive audit logs for the Asset Registry
"""
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random
import json

db = SessionLocal()

try:
    print("\n🔍 Generating Comprehensive Audit Logs...\n")

    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()

    if not users or not assets:
        print("❌ Run seed_data.py and seed_large_dataset.py first!")
        exit(1)

    print(f"Found {len(users)} users and {len(assets)} assets\n")

    # Clear existing audit logs
    db.query(models.AuditLog).delete()
    db.commit()
    print("  ✓ Cleared existing audit logs\n")

    # Action templates
    actions = {
        "Asset": [
            ("CREATE", "Asset created"),
            ("UPDATE", "Asset updated"),
            ("DELETE", "Asset deleted"),
            ("VIEW", "Asset viewed"),
        ],
        "User": [
            ("LOGIN", "User logged in"),
            ("LOGOUT", "User logged out"),
            ("UPDATE", "User profile updated"),
            ("VIEW", "User profile viewed"),
        ],
        "Domain": [
            ("CREATE", "Domain created"),
            ("UPDATE", "Domain updated"),
            ("VIEW", "Domain viewed"),
        ],
    }

    # User agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    audit_logs = []
    log_count = 0

    # Generate audit logs for assets
    print("📝 Generating asset-related audit logs...\n")

    for asset in assets:
        # Asset CREATE log
        create_user = random.choice(users)
        create_time = asset.created_at

        audit_log = models.AuditLog(
            user_id=create_user.user_id,
            action="CREATE",
            entity_type="Asset",
            entity_id=asset.asset_id,
            old_value=None,
            new_value=json.dumps({
                "asset_name": asset.asset_name,
                "environment": asset.environment,
                "lifecycle_stage": asset.lifecycle_stage,
                "version": asset.version,
                "naming_compliant": asset.naming_compliant,
            }),
            timestamp=create_time,
            ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            user_agent=random.choice(user_agents),
        )
        db.add(audit_log)
        audit_logs.append(audit_log)
        log_count += 1

        # Random VIEW logs (2-5 views per asset)
        num_views = random.randint(2, 5)
        for _ in range(num_views):
            view_user = random.choice(users)
            view_time = create_time + timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            audit_log = models.AuditLog(
                user_id=view_user.user_id,
                action="VIEW",
                entity_type="Asset",
                entity_id=asset.asset_id,
                old_value=None,
                new_value=None,
                timestamp=view_time,
                ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent=random.choice(user_agents),
            )
            db.add(audit_log)
            audit_logs.append(audit_log)
            log_count += 1

        # Random UPDATE logs (0-3 updates per asset)
        num_updates = random.randint(0, 3)
        previous_version = asset.version
        previous_lifecycle = asset.lifecycle_stage

        for i in range(num_updates):
            update_user = random.choice(users)
            update_time = create_time + timedelta(
                days=random.randint(10, 60),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Generate realistic update
            new_version = previous_version
            new_lifecycle = previous_lifecycle

            update_type = random.choice(["version", "lifecycle", "both"])

            old_data = {
                "version": previous_version,
                "lifecycle_stage": previous_lifecycle,
            }

            if update_type in ["version", "both"]:
                # Increment version
                if "." in previous_version:
                    major, minor = previous_version.replace("v", "").split(".")
                    new_version = f"v{major}.{int(minor) + 1}"
                else:
                    major = int(previous_version.replace("v", ""))
                    new_version = f"v{major}.1"

            if update_type in ["lifecycle", "both"]:
                # Advance lifecycle
                lifecycle_progression = {
                    "Draft": "Active",
                    "Active": random.choice(["Active", "Deprecated"]),
                    "Deprecated": random.choice(["Deprecated", "Retired"]),
                    "Retired": "Retired",
                }
                new_lifecycle = lifecycle_progression.get(previous_lifecycle, previous_lifecycle)

            new_data = {
                "version": new_version,
                "lifecycle_stage": new_lifecycle,
            }

            if old_data != new_data:
                audit_log = models.AuditLog(
                    user_id=update_user.user_id,
                    action="UPDATE",
                    entity_type="Asset",
                    entity_id=asset.asset_id,
                    old_value=json.dumps(old_data),
                    new_value=json.dumps(new_data),
                    timestamp=update_time,
                    ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    user_agent=random.choice(user_agents),
                )
                db.add(audit_log)
                audit_logs.append(audit_log)
                log_count += 1

                previous_version = new_version
                previous_lifecycle = new_lifecycle

        if log_count % 100 == 0:
            print(f"  ✓ Created {log_count} audit logs...")

    # Generate user login/logout logs
    print("\n👤 Generating user activity logs...\n")

    base_date = datetime.utcnow() - timedelta(days=60)

    for user in users:
        # Generate 10-20 login sessions per user
        num_sessions = random.randint(10, 20)

        for _ in range(num_sessions):
            login_time = base_date + timedelta(
                days=random.randint(0, 60),
                hours=random.randint(7, 18),  # Business hours
                minutes=random.randint(0, 59)
            )

            # LOGIN
            audit_log = models.AuditLog(
                user_id=user.user_id,
                action="LOGIN",
                entity_type="User",
                entity_id=user.user_id,
                old_value=None,
                new_value=json.dumps({"username": user.username, "email": user.email}),
                timestamp=login_time,
                ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent=random.choice(user_agents),
            )
            db.add(audit_log)
            log_count += 1

            # LOGOUT (few hours later)
            if random.random() > 0.2:  # 80% logout
                logout_time = login_time + timedelta(hours=random.randint(1, 8))
                audit_log = models.AuditLog(
                    user_id=user.user_id,
                    action="LOGOUT",
                    entity_type="User",
                    entity_id=user.user_id,
                    old_value=None,
                    new_value=None,
                    timestamp=logout_time,
                    ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    user_agent=random.choice(user_agents),
                )
                db.add(audit_log)
                log_count += 1

    db.commit()

    print(f"\n  ✓ Created total {log_count} audit logs")

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Audit Logs Created Successfully!")
    print(f"{'='*60}")
    print(f"📊 Total Audit Logs: {log_count}")

    # Count by action
    from sqlalchemy import func
    actions_count = (
        db.query(models.AuditLog.action, func.count(models.AuditLog.log_id))
        .group_by(models.AuditLog.action)
        .all()
    )

    print(f"\n📈 By Action:")
    for action, count in sorted(actions_count, key=lambda x: x[1], reverse=True):
        print(f"   - {action}: {count} logs")

    # Count by entity type
    entities_count = (
        db.query(models.AuditLog.entity_type, func.count(models.AuditLog.log_id))
        .group_by(models.AuditLog.entity_type)
        .all()
    )

    print(f"\n🎯 By Entity Type:")
    for entity, count in sorted(entities_count, key=lambda x: x[1], reverse=True):
        print(f"   - {entity}: {count} logs")

    print(f"{'='*60}\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
