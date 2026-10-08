#!/usr/bin/env python3
"""Seed only the remaining tools tables that have no data"""

import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, models_extended, models_advanced, models_integrations, models_itsm, models_collaboration

def seed_remaining_tools():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("  🚀 SEEDING REMAINING TOOLS DATA")
        print("=" * 70)
        print()

        # Check Tasks count
        tasks_count = db.query(models_collaboration.Task).count()
        if tasks_count == 0:
            print(f"Adding 50 Tasks...")
            tasks = []

            # Get existing initiative IDs
            initiative_ids = [i.initiative_id for i in db.query(models_extended.StrategicInitiative.initiative_id).all()]

            for i in range(1, 51):
                created_days_ago = random.randint(0, 30)
                due_days = random.randint(1, 14)
                priority = random.choice([models_collaboration.TaskPriority.LOW, models_collaboration.TaskPriority.MEDIUM,
                                        models_collaboration.TaskPriority.HIGH, models_collaboration.TaskPriority.CRITICAL])
                status = random.choice([models_collaboration.TaskStatus.TODO, models_collaboration.TaskStatus.IN_PROGRESS,
                                      models_collaboration.TaskStatus.IN_REVIEW, models_collaboration.TaskStatus.DONE])

                task = models_collaboration.Task(
                    title=f"Task {i}: Review Asset Configuration",
                    description=f"Task to review and validate asset configuration for compliance. Task ID: {i}",
                    assigned_to=random.randint(1, 4),
                    created_by=random.randint(1, 4),
                    initiative_id=random.choice(initiative_ids) if initiative_ids and random.random() > 0.5 else None,
                    due_date=(datetime.utcnow() + timedelta(days=due_days)).date(),
                    start_date=(datetime.utcnow() - timedelta(days=created_days_ago)).date() if random.random() > 0.3 else None,
                    priority=priority,
                    status=status,
                    completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)) if status == models_collaboration.TaskStatus.DONE else None,
                    estimated_hours=random.randint(1, 40),
                    actual_hours=random.randint(1, 40) if status == models_collaboration.TaskStatus.DONE else None,
                    tags="governance,compliance" if random.random() > 0.5 else "review,quality",
                    created_at=datetime.utcnow() - timedelta(days=created_days_ago),
                    updated_at=datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago))
                )
                tasks.append(task)

            db.bulk_save_objects(tasks)
            db.commit()
            print(f"✓ Created {len(tasks)} tasks")
        else:
            print(f"✓ Tasks already exist ({tasks_count} records), skipping...")

        # Check Notifications count
        notifications_count = db.query(models_collaboration.Notification).count()
        if notifications_count == 0:
            print(f"Adding 100 Notifications...")
            notifications = []

            for i in range(1, 101):
                created_days_ago = random.randint(0, 30)
                priority = random.choice([models_collaboration.TaskPriority.LOW, models_collaboration.TaskPriority.MEDIUM,
                                        models_collaboration.TaskPriority.HIGH, models_collaboration.TaskPriority.CRITICAL])
                notif_type = random.choice([models_collaboration.NotificationType.TASK_ASSIGNED,
                                          models_collaboration.NotificationType.TASK_UPDATED,
                                          models_collaboration.NotificationType.APPROVAL_NEEDED,
                                          models_collaboration.NotificationType.VIOLATION_DETECTED])
                is_read = random.choice([True, False])
                entity_type = random.choice([models_collaboration.EntityType.ASSET, models_collaboration.EntityType.TASK,
                                           models_collaboration.EntityType.CHANGE_REQUEST])

                notification = models_collaboration.Notification(
                    user_id=random.randint(1, 4),
                    type=notif_type,
                    title=f"Notification {i}: {notif_type.value.replace('_', ' ').title()}",
                    message=f"This is notification #{i} about {notif_type.value}. Please review.",
                    link=f"/assets/{random.randint(1, 5)}" if random.random() > 0.5 else None,
                    entity_type=entity_type if random.random() > 0.3 else None,
                    entity_id=random.randint(1, 20) if random.random() > 0.3 else None,
                    priority=priority,
                    read=is_read,
                    read_at=datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago)) if is_read else None,
                    created_at=datetime.utcnow() - timedelta(days=created_days_ago)
                )
                notifications.append(notification)

            db.bulk_save_objects(notifications)
            db.commit()
            print(f"✓ Created {len(notifications)} notifications")
        else:
            print(f"✓ Notifications already exist ({notifications_count} records), skipping...")

        # Check Comments count
        comments_count = db.query(models_collaboration.Comment).count()
        if comments_count == 0:
            print(f"Adding 75 Comments...")
            comments = []

            for i in range(1, 76):
                created_days_ago = random.randint(0, 30)
                entity_type = random.choice([models_collaboration.EntityType.ASSET, models_collaboration.EntityType.CHANGE_REQUEST,
                                           models_collaboration.EntityType.TASK, models_collaboration.EntityType.INITIATIVE])
                is_edited = random.choice([True, False])

                comment = models_collaboration.Comment(
                    entity_type=entity_type,
                    entity_id=random.randint(1, 10),
                    user_id=random.randint(1, 4),
                    comment_text=f"Comment {i}: This is a sample comment about the {entity_type.value}. The review looks good and I approve this change.",
                    parent_comment_id=random.randint(1, i-1) if i > 10 and random.random() > 0.7 else None,
                    mentioned_users=f"{random.randint(1,4)},{random.randint(1,4)}" if random.random() > 0.7 else None,
                    edited=is_edited,
                    deleted=False,
                    created_at=datetime.utcnow() - timedelta(days=created_days_ago),
                    updated_at=datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago)) if is_edited else datetime.utcnow() - timedelta(days=created_days_ago)
                )
                comments.append(comment)

            db.bulk_save_objects(comments)
            db.commit()
            print(f"✓ Created {len(comments)} comments")
        else:
            print(f"✓ Comments already exist ({comments_count} records), skipping...")

        # Check Activity Logs count
        activity_logs_count = db.query(models_collaboration.ActivityLog).count()
        if activity_logs_count == 0:
            print(f"Adding 200 Activity Logs...")
            activity_logs = []

            for i in range(1, 201):
                created_days_ago = random.randint(0, 60)
                entity_type = random.choice([models_collaboration.EntityType.ASSET, models_collaboration.EntityType.CHANGE_REQUEST,
                                           models_collaboration.EntityType.TASK, models_collaboration.EntityType.INITIATIVE])
                action = random.choice([models_collaboration.ActivityAction.CREATED, models_collaboration.ActivityAction.UPDATED,
                                      models_collaboration.ActivityAction.APPROVED, models_collaboration.ActivityAction.STATUS_CHANGED])

                activity_log = models_collaboration.ActivityLog(
                    user_id=random.randint(1, 4),
                    action=action,
                    entity_type=entity_type,
                    entity_id=random.randint(1, 20),
                    entity_name=f"{entity_type.value.title()} #{random.randint(1, 20)}",
                    description=f"User {action.value} {entity_type.value} #{random.randint(1, 20)}",
                    meta_data='{"field": "status", "old_value": "pending", "new_value": "approved"}' if action == models_collaboration.ActivityAction.UPDATED else None,
                    created_at=datetime.utcnow() - timedelta(days=created_days_ago)
                )
                activity_logs.append(activity_log)

            db.bulk_save_objects(activity_logs)
            db.commit()
            print(f"✓ Created {len(activity_logs)} activity logs")
        else:
            print(f"✓ Activity Logs already exist ({activity_logs_count} records), skipping...")

        # Check Governance Policies count
        policies_count = db.query(models_advanced.GovernancePolicy).count()
        if policies_count == 0:
            print(f"Adding 15 Governance Policies...")
            policies = []
            policy_types = [models_advanced.PolicyType.NAMING_CONVENTION,
                          models_advanced.PolicyType.QUALITY_THRESHOLD,
                          models_advanced.PolicyType.SECURITY_SCAN,
                          models_advanced.PolicyType.DATA_CLASSIFICATION,
                          models_advanced.PolicyType.SLA_REQUIREMENT]

            policy_names = [
                "Asset Naming Standard", "Environment Code Policy", "Domain Classification",
                "Data Quality Threshold", "Completeness Requirements", "Accuracy Standards",
                "Access Control Policy", "Encryption Requirements", "PII Handling",
                "Data Retention 7 Years", "Log Retention 90 Days", "Backup Retention",
                "SLA Response Time", "Uptime Requirements", "Change Management"
            ]

            for i, name in enumerate(policy_names, 1):
                policy = models_advanced.GovernancePolicy(
                    policy_name=name,
                    policy_type=random.choice(policy_types),
                    description=f"Policy for {name.lower()} governance and compliance",
                    policy_definition='{"rules": [{"field": "asset_name", "pattern": "^(DEV|QA|UAT|PROD)-.+"}]}',
                    is_active=random.choice([True, True, True, False]),
                    is_blocking=random.choice([True, False]),
                    enforcement_level=random.choice(["advisory", "warning", "blocking"]),
                    applies_to_domains='["HR", "FIN", "OPS"]' if random.random() > 0.5 else None,
                    applies_to_environments='["PROD", "QA"]' if random.random() > 0.5 else None,
                    exemption_allowed=random.choice([True, False]),
                    exemption_requires_approval=random.choice([True, False]),
                    created_by=1,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                    updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                policies.append(policy)

            db.bulk_save_objects(policies)
            db.commit()
            print(f"✓ Created {len(policies)} governance policies")
        else:
            print(f"✓ Governance Policies already exist ({policies_count} records), skipping...")

        # Check Policy Validations count
        policy_validations_count = db.query(models_advanced.PolicyValidation).count()
        if policy_validations_count == 0:
            print(f"Adding 100 Policy Validations...")
            policy_ids = [p.policy_id for p in db.query(models_advanced.GovernancePolicy.policy_id).all()]
            if policy_ids:
                validations = []

                for i in range(1, 101):
                    validated_days_ago = random.randint(0, 30)
                    passed = random.choice([True, True, True, False])
                    exemption_requested = random.choice([True, False]) if not passed else False

                    validation = models_advanced.PolicyValidation(
                        policy_id=random.choice(policy_ids),
                        asset_id=random.randint(1, 5),
                        validated_at=datetime.utcnow() - timedelta(days=validated_days_ago),
                        passed=passed,
                        violations='[{"field": "asset_name", "message": "Asset name does not follow naming convention", "severity": "high"}]' if not passed else None,
                        deployment_blocked=not passed if random.random() > 0.5 else False,
                        exemption_requested=exemption_requested,
                        exemption_approved=random.choice([True, False]) if exemption_requested else False,
                        exemption_approver=random.randint(1, 3) if exemption_requested else None,
                        exemption_reason="Business critical deployment, naming standard will be fixed in next release" if exemption_requested else None
                    )
                    validations.append(validation)

                db.bulk_save_objects(validations)
                db.commit()
                print(f"✓ Created {len(validations)} policy validations")
            else:
                print("⚠ No policies found, skipping policy validations...")
        else:
            print(f"✓ Policy Validations already exist ({policy_validations_count} records), skipping...")

        print()
        print("=" * 70)
        print("  ✓ Successfully seeded remaining tools data!")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding remaining tools data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_remaining_tools()
