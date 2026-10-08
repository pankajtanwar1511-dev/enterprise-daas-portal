#!/usr/bin/env python3
"""
Quick Fix: Reset Tasks Table to Start from ID 1
This script deletes existing tasks and recreates them starting from ID 1.
"""

import sys
from datetime import datetime, timedelta
import random
from sqlalchemy import text
from app.database import SessionLocal
from app import models  # Import all models to avoid relationship errors
from app.models_collaboration import Task, TaskPriority, TaskStatus
from app.models_extended import StrategicInitiative

def fix_tasks_sequence():
    db = SessionLocal()
    try:
        print("="*70)
        print("  FIXING TASKS TABLE - Resetting to Start from ID 1")
        print("="*70)

        # Delete all existing tasks
        existing_count = db.query(Task).count()
        print(f"\n1. Found {existing_count} existing tasks - deleting...")
        db.query(Task).delete()
        db.commit()
        print(f"   ✓ Deleted {existing_count} tasks")

        # Reset sequence to start from 1
        print(f"\n2. Resetting task_id sequence to 1...")
        db.execute(text("ALTER SEQUENCE tasks_task_id_seq RESTART WITH 1"))
        db.commit()
        print(f"   ✓ Sequence reset")

        # Get initiative IDs for relationships
        initiative_ids = [i.initiative_id for i in db.query(StrategicInitiative.initiative_id).all()]
        print(f"\n3. Creating 50 new tasks starting from ID 1...")

        tasks = []
        for i in range(1, 51):
            created_days_ago = random.randint(0, 30)
            due_days = random.randint(1, 14)
            priority = random.choice([TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.CRITICAL])
            status = random.choice([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW, TaskStatus.DONE])

            task = Task(
                title=f"Task {i}: Review Asset Configuration",
                description=f"Task to review and validate asset configuration for compliance. Task number: {i}",
                assigned_to=random.randint(1, 4),
                created_by=random.randint(1, 4),
                initiative_id=random.choice(initiative_ids) if initiative_ids and random.random() > 0.5 else None,
                due_date=(datetime.utcnow() + timedelta(days=due_days)).date(),
                start_date=(datetime.utcnow() - timedelta(days=created_days_ago)).date() if random.random() > 0.3 else None,
                priority=priority,
                status=status,
                completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)) if status == TaskStatus.DONE else None,
                estimated_hours=random.randint(1, 40),
                actual_hours=random.randint(1, 40) if status == TaskStatus.DONE else None,
                tags="governance,compliance" if random.random() > 0.5 else "review,quality",
                created_at=datetime.utcnow() - timedelta(days=created_days_ago),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago))
            )
            tasks.append(task)

        db.bulk_save_objects(tasks)
        db.commit()
        print(f"   ✓ Created {len(tasks)} tasks")

        # Verify IDs
        first_task = db.query(Task).order_by(Task.task_id).first()
        last_task = db.query(Task).order_by(Task.task_id.desc()).first()
        total = db.query(Task).count()

        print(f"\n4. Verification:")
        print(f"   - First task ID: {first_task.task_id}")
        print(f"   - Last task ID: {last_task.task_id}")
        print(f"   - Total tasks: {total}")

        if first_task.task_id == 1:
            print(f"\n✅ SUCCESS! Tasks now start from ID 1")
        else:
            print(f"\n❌ ERROR: Tasks still don't start from ID 1!")
            sys.exit(1)

        print("\n" + "="*70)
        print("  ✓ Tasks table fixed successfully!")
        print("="*70)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error fixing tasks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_tasks_sequence()
