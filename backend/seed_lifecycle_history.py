"""
Seed lifecycle history data for existing assets
"""
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

try:
    print("\n🕐 Adding Lifecycle History Data...\n")

    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()

    if not users or not assets:
        print("❌ Run seed_data.py first to create users and assets!")
        exit(1)

    # Lifecycle stage transitions (realistic progression)
    lifecycle_transitions = [
        {
            "from": None,
            "to": "Draft",
            "reasons": [
                "Initial asset registration",
                "New asset proposal created",
                "Asset creation approved by data steward",
            ]
        },
        {
            "from": "Draft",
            "to": "Active",
            "reasons": [
                "Asset deployed to production environment",
                "All validation checks passed, asset activated",
                "Business approval received, moved to active",
                "Development completed, promoted to active",
            ]
        },
        {
            "from": "Active",
            "to": "Deprecated",
            "reasons": [
                "Asset replaced by newer version",
                "Business requirements changed, asset deprecated",
                "Technology stack migration planned",
                "Performance issues, deprecation initiated",
            ]
        },
        {
            "from": "Deprecated",
            "to": "Retired",
            "reasons": [
                "Deprecation period completed, asset retired",
                "No longer in use, safely decommissioned",
                "Migration to replacement system completed",
                "Data archived, asset permanently retired",
            ]
        },
        {
            "from": "Active",
            "to": "Active",
            "reasons": [
                "Configuration updated, revalidated as active",
                "Security patches applied",
                "Performance optimization completed",
                "Documentation updated",
            ]
        },
    ]

    history_count = 0

    for asset in assets:
        # Get current lifecycle stage
        current_stage = asset.lifecycle_stage

        # Create 2-5 history entries per asset
        num_entries = random.randint(2, 5)

        # Build realistic history based on current stage
        if current_stage == "Draft":
            # Only initial creation
            transitions = [
                (None, "Draft")
            ]
        elif current_stage == "Active":
            # Draft → Active, possibly with some updates
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
            ]
            # Add some updates while active
            for _ in range(random.randint(0, 2)):
                transitions.append(("Active", "Active"))
        elif current_stage == "Deprecated":
            # Draft → Active → Deprecated
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
                ("Active", "Deprecated"),
            ]
        elif current_stage == "Retired":
            # Full lifecycle
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
                ("Active", "Deprecated"),
                ("Deprecated", "Retired"),
            ]

        # Limit to num_entries
        transitions = transitions[:num_entries]

        # Create history entries with realistic timestamps
        base_date = asset.created_at
        days_between = 30  # 30 days between each transition

        for i, (from_state, to_state) in enumerate(transitions):
            # Find matching transition template
            matching_transition = next(
                (t for t in lifecycle_transitions if t["from"] == from_state and t["to"] == to_state),
                None
            )

            if matching_transition:
                reason = random.choice(matching_transition["reasons"])
            else:
                reason = f"Transitioned from {from_state or 'initial'} to {to_state}"

            # Calculate timestamp (progressively later)
            changed_at = base_date + timedelta(days=i * days_between)

            history = models.LifecycleHistory(
                asset_id=asset.asset_id,
                from_state=from_state,
                to_state=to_state,
                changed_by=random.choice(users).user_id,
                change_reason=reason,
                changed_at=changed_at
            )
            db.add(history)
            history_count += 1

    db.commit()
    print(f"  ✓ Created {history_count} lifecycle history entries for {len(assets)} assets")

    print("\n✅ Lifecycle history data seeded successfully!\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
