"""
Seed script to create 100+ diverse assets with extensive lifecycle histories
"""
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

try:
    print("\n🚀 Generating Large Dataset (100+ Assets)...\n")

    # Get existing data
    users = db.query(models.User).all()
    domains = db.query(models.Domain).all()

    if not users or not domains:
        print("❌ Run seed_data.py first to create users and domains!")
        exit(1)

    print(f"Found {len(users)} users and {len(domains)} domains\n")

    # Asset name templates by domain
    asset_templates = {
        "HR": ["HRMS", "PayrollDB", "EmployeePortal", "TimeTracking", "BenefitsDB", "PerformanceDB", "RecruitmentAPI", "OnboardingApp"],
        "FIN": ["GeneralLedger", "AccountsPayable", "AccountsReceivable", "BudgetDB", "ExpenseTracker", "InvoiceAPI", "TaxDB", "AuditLog"],
        "OPS": ["SupplyChainDB", "InventoryMgmt", "OrderProcessing", "WarehouseDB", "ShippingAPI", "ProcurementDB", "LogisticsApp", "VendorPortal"],
        "SALES": ["CRM", "SalesForceDB", "OpportunityTracker", "QuoteGenerator", "CustomerPortal", "LeadMgmt", "SalesAnalytics", "PipelineDB"],
        "IT": ["AssetMgmt", "TicketingSystem", "MonitoringDB", "ConfigMgmt", "NetworkDB", "SecurityLog", "BackupSystem", "DeploymentAPI"],
        "DATA": ["DataLake", "DataWarehouse", "ETL", "AnalyticsDB", "ReportingAPI", "DataCatalog", "MLPipeline", "StreamProcessor"]
    }

    # System type suffixes
    suffixes = ["DW", "DB", "API", "ETL", "App", "Portal", "Service", "Platform", "Engine", "Hub"]

    # Environments
    environments = ["DEV", "QA", "UAT", "PROD"]

    # Lifecycle stages with weights (higher weight = more common)
    lifecycle_stages = [
        ("Active", 50),      # 50% active
        ("Draft", 20),       # 20% draft
        ("Deprecated", 20),  # 20% deprecated
        ("Retired", 10)      # 10% retired
    ]

    # Descriptions templates
    descriptions = [
        "Enterprise-grade {} system for {}",
        "Mission-critical {} platform supporting {}",
        "Scalable {} solution for {} operations",
        "Cloud-native {} service handling {}",
        "Legacy {} system migrating to cloud",
        "Modern {} platform with real-time {}",
        "Containerized {} microservice for {}",
        "Data-driven {} analytics for {}"
    ]

    business_justifications = [
        "Supports core business operations and reporting requirements",
        "Enables digital transformation initiative",
        "Reduces operational costs through automation",
        "Improves customer experience and satisfaction",
        "Ensures regulatory compliance and data governance",
        "Drives revenue growth through better insights",
        "Enhances employee productivity and collaboration",
        "Mitigates security risks and vulnerabilities"
    ]

    created_assets = []
    asset_count = 0
    existing_names = set()  # Track generated names to avoid duplicates

    # Generate 100 assets (mix of compliant and non-compliant)
    for i in range(100):
        # Choose random domain
        domain = random.choice(domains)
        domain_code = domain.domain_code

        # Choose environment with weighted randomness (more PROD and QA)
        env_weights = [15, 35, 25, 25]  # DEV, QA, UAT, PROD
        environment = random.choices(environments, weights=env_weights)[0]

        # Choose lifecycle stage with weights
        lifecycle_stage = random.choices(
            [stage for stage, _ in lifecycle_stages],
            weights=[weight for _, weight in lifecycle_stages]
        )[0]

        # Choose template
        if domain_code in asset_templates:
            template = random.choice(asset_templates[domain_code])
        else:
            template = "System"

        # Add suffix
        suffix = random.choice(suffixes)

        # Version
        version = f"v{random.randint(1, 5)}"
        if random.random() > 0.7:  # 30% have minor versions
            version += f".{random.randint(0, 9)}"

        # Decide if compliant (70% compliant, 30% non-compliant)
        is_compliant = random.random() < 0.7

        if is_compliant:
            # Build compliant name: ENV-DOMAIN-SYSTEM-VERSION
            asset_name = f"{environment}-{domain_code}-{template}-{suffix}-{version}"
        else:
            # Generate non-compliant name (various violations)
            violation_type = random.randint(1, 5)
            if violation_type == 1:
                # Lowercase
                asset_name = f"{environment.lower()}-{domain_code.lower()}-{template}-{version}"
            elif violation_type == 2:
                # Missing version
                asset_name = f"{environment}-{domain_code}-{template}"
            elif violation_type == 3:
                # Wrong format (spaces)
                asset_name = f"{environment} {domain_code} {template}"
            elif violation_type == 4:
                # Missing environment
                asset_name = f"{domain_code}-{template}-{version}"
            else:
                # Random invalid name
                asset_name = f"legacy_{template}_{random.randint(1, 999)}"

        # Ensure name is unique (both in DB and in current batch)
        attempt = 0
        original_name = asset_name
        while (asset_name in existing_names or
               db.query(models.Asset).filter(models.Asset.asset_name == asset_name).first()):
            attempt += 1
            asset_name = f"{original_name}-{i}-{attempt}"

        existing_names.add(asset_name)

        # Generate description
        desc_template = random.choice(descriptions)
        business_area = domain.domain_name.lower()
        desc = desc_template.format(suffix.lower(), business_area)

        # Create asset
        asset = models.Asset(
            asset_name=asset_name,
            domain_id=domain.domain_id,
            environment=environment,
            owner_id=random.choice(users).user_id,
            version=version,
            lifecycle_stage=lifecycle_stage,
            documentation_url=f"https://docs.company.com/{template.lower()}" if random.random() > 0.3 else None,
            description=desc,
            business_justification=random.choice(business_justifications),
            tags='["automation", "cloud"]' if random.random() > 0.5 else None,
            naming_compliant=is_compliant,
            compliance_check_date=datetime.utcnow(),
            created_by=random.choice(users).user_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730))  # Created 1 month to 2 years ago
        )

        db.add(asset)
        created_assets.append(asset)
        asset_count += 1

        if asset_count % 20 == 0:
            print(f"  ✓ Created {asset_count} assets...")

    db.commit()
    print(f"\n  ✓ Created total {asset_count} assets")

    # Refresh to get IDs
    for asset in created_assets:
        db.refresh(asset)

    # Generate lifecycle histories (5-10 entries per asset)
    print("\n📜 Generating lifecycle histories...\n")

    lifecycle_transitions = [
        {
            "from": None,
            "to": "Draft",
            "reasons": [
                "Initial asset registration in governance portal",
                "New asset proposal created by data steward",
                "Asset creation approved by architecture review board",
                "System design documentation completed",
            ]
        },
        {
            "from": "Draft",
            "to": "Active",
            "reasons": [
                "Asset deployed to production environment successfully",
                "All validation checks passed, asset activated",
                "Business approval received, moved to active status",
                "Development and testing completed, promoted to active",
                "Security audit completed, approved for production use",
            ]
        },
        {
            "from": "Active",
            "to": "Active",
            "reasons": [
                "Security patches applied and validated",
                "Configuration updated per change request CR-{}".format(random.randint(1000, 9999)),
                "Documentation updated with latest changes",
                "Performance optimization completed",
                "Backup and recovery procedures validated",
                "Annual security review completed successfully",
                "Compliance audit passed, no issues found",
                "Capacity increased to handle growing demand",
                "Integration with new upstream system completed",
                "Database schema updated for new features",
            ]
        },
        {
            "from": "Active",
            "to": "Deprecated",
            "reasons": [
                "Asset replaced by newer version {}".format(f"v{random.randint(2, 6)}"),
                "Business requirements changed, asset deprecated",
                "Technology stack migration to cloud planned",
                "Performance issues identified, deprecation initiated",
                "End of vendor support announced, replacement planned",
                "Consolidation with other systems approved",
            ]
        },
        {
            "from": "Deprecated",
            "to": "Retired",
            "reasons": [
                "Deprecation period completed, asset safely retired",
                "No longer in use by any business unit",
                "Migration to replacement system completed successfully",
                "Data archived to long-term storage, asset retired",
                "Decommissioning plan executed, hardware released",
            ]
        },
        {
            "from": "Deprecated",
            "to": "Active",
            "reasons": [
                "Business requirement changed, asset reactivated",
                "Replacement system failed, reverted to this asset",
                "Emergency business need, temporarily reactivated",
            ]
        },
    ]

    history_count = 0
    for asset in created_assets:
        current_stage = asset.lifecycle_stage

        # Determine how many history entries (5-10)
        num_entries = random.randint(5, 10)

        # Build realistic history progression
        transitions = []

        if current_stage == "Draft":
            # Only initial creation
            transitions = [(None, "Draft")]
            # Add some updates while in draft
            for _ in range(num_entries - 1):
                transitions.append(("Draft", "Draft"))

        elif current_stage == "Active":
            # Draft → Active, with updates
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
            ]
            # Add updates while active
            for _ in range(num_entries - 2):
                transitions.append(("Active", "Active"))

        elif current_stage == "Deprecated":
            # Draft → Active → Deprecated
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
            ]
            # Some updates while active
            for _ in range(max(1, num_entries - 4)):
                transitions.append(("Active", "Active"))
            transitions.append(("Active", "Deprecated"))
            # Maybe some updates while deprecated
            if num_entries > len(transitions):
                for _ in range(num_entries - len(transitions)):
                    transitions.append(("Deprecated", "Deprecated"))

        elif current_stage == "Retired":
            # Full lifecycle
            transitions = [
                (None, "Draft"),
                ("Draft", "Active"),
            ]
            # Updates while active
            for _ in range(max(1, num_entries - 5)):
                transitions.append(("Active", "Active"))
            transitions.append(("Active", "Deprecated"))
            # Maybe update while deprecated
            if num_entries > len(transitions) + 1:
                transitions.append(("Deprecated", "Deprecated"))
            transitions.append(("Deprecated", "Retired"))

        # Ensure we have exactly num_entries transitions
        while len(transitions) < num_entries:
            # Add updates to current stage
            transitions.insert(-1, (current_stage, current_stage))

        transitions = transitions[:num_entries]

        # Create history entries with realistic timestamps
        base_date = asset.created_at
        days_between = max(5, (datetime.utcnow() - base_date).days // (num_entries + 1))

        for i, (from_state, to_state) in enumerate(transitions):
            # Find matching transition template
            matching = next(
                (t for t in lifecycle_transitions if t["from"] == from_state and t["to"] == to_state),
                None
            )

            if matching:
                reason = random.choice(matching["reasons"])
            else:
                # Generic reason for self-transitions
                if from_state == to_state:
                    reason = f"Routine maintenance and validation completed for {to_state} system"
                else:
                    reason = f"Transitioned from {from_state or 'initial'} to {to_state}"

            # Calculate progressive timestamp
            changed_at = base_date + timedelta(days=i * days_between, hours=random.randint(0, 23), minutes=random.randint(0, 59))

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

        if history_count % 100 == 0:
            print(f"  ✓ Created {history_count} lifecycle history entries...")

    db.commit()
    print(f"\n  ✓ Created total {history_count} lifecycle history entries")

    # Summary
    compliant_count = sum(1 for a in created_assets if a.naming_compliant)
    non_compliant_count = asset_count - compliant_count

    print(f"\n{'='*60}")
    print(f"✅ Large Dataset Created Successfully!")
    print(f"{'='*60}")
    print(f"📊 Assets Created: {asset_count}")
    print(f"   - Compliant: {compliant_count} ({compliant_count/asset_count*100:.1f}%)")
    print(f"   - Non-compliant: {non_compliant_count} ({non_compliant_count/asset_count*100:.1f}%)")
    print(f"\n📈 Lifecycle Histories: {history_count} entries")
    print(f"   - Average per asset: {history_count/asset_count:.1f} entries")
    print(f"\n🌍 Environments:")
    for env in environments:
        count = sum(1 for a in created_assets if a.environment == env)
        print(f"   - {env}: {count} assets")
    print(f"\n🎯 Lifecycle Stages:")
    for stage, _ in lifecycle_stages:
        count = sum(1 for a in created_assets if a.lifecycle_stage == stage)
        print(f"   - {stage}: {count} assets")
    print(f"{'='*60}\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
