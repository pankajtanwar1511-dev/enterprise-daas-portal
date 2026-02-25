"""
Seed All Advanced Features - Corrected Version
Populates all missing data for Features 4-15
"""
from app.database import SessionLocal
from app import models, models_extended, models_advanced, models_integrations
from datetime import datetime, timedelta
import random
import secrets
import hashlib
import json

db = SessionLocal()

try:
    print("\n" + "="*70)
    print("  🚀 POPULATING ALL ADVANCED FEATURES")
    print("="*70 + "\n")

    # Get existing data
    users = db.query(models.User).all()
    assets = db.query(models.Asset).all()
    vendors = db.query(models_extended.Vendor).all()
    domains = db.query(models.Domain).all()

    if not users or not assets:
        print("❌ Base data missing!")
        exit(1)

    print(f"Found: {len(users)} users, {len(assets)} assets, {len(vendors)} vendors\n")

    # =========================================================================
    # WEBHOOKS - Feature 10
    # =========================================================================
    print("🪝 Seeding Webhooks...")
    db.query(models_integrations.Webhook).delete()
    db.query(models_integrations.WebhookDelivery).delete()

    webhooks = [
        models_integrations.Webhook(
            name="Slack Compliance Alerts",
            url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            secret=secrets.token_hex(32),
            events=["compliance.violation", "compliance.resolved"],
            active=True,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        models_integrations.Webhook(
            name="PagerDuty SLA Alerts",
            url="https://events.pagerduty.com/integration/abc123/enqueue",
            secret=secrets.token_hex(32),
            events=["sla.violation", "sla.breach.critical"],
            active=True,
            created_by=users[1].user_id if len(users) > 1 else users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=45)
        ),
        models_integrations.Webhook(
            name="Asset Change Notifications",
            url="https://api.company.com/webhooks/asset-changes",
            secret=secrets.token_hex(32),
            events=["asset.created", "asset.updated", "asset.deleted"],
            active=True,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
    ]
    db.add_all(webhooks)
    db.commit()

    # Webhook deliveries
    deliveries = []
    for webhook in webhooks:
        for _ in range(random.randint(10, 25)):
            success = random.random() > 0.1
            delivered_at = datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            delivery = models_integrations.WebhookDelivery(
                webhook_id=webhook.webhook_id,
                event=random.choice(webhook.events),
                payload={"asset_id": random.randint(1, 10), "timestamp": str(delivered_at)},
                status_code=200 if success else random.choice([500, 502, 504]),
                response_body="OK" if success else "Internal Server Error",
                success=success,
                delivered_at=delivered_at,
                duration_ms=random.randint(50, 500)
            )
            deliveries.append(delivery)

    db.add_all(deliveries)
    db.commit()
    print(f"  ✓ Created {len(webhooks)} webhooks with {len(deliveries)} deliveries\n")

    # =========================================================================
    # API KEYS - Feature 9
    # =========================================================================
    print("🔑 Seeding API Keys...")
    db.query(models_integrations.APIKey).delete()

    def generate_api_key():
        random_part = secrets.token_urlsafe(30)
        full_key = f"gp_{random_part}"
        key_prefix = full_key[:10]
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        return full_key, key_prefix, key_hash

    api_keys = []
    for i, user in enumerate(users[:4]):
        _, prefix, key_hash = generate_api_key()
        api_key = models_integrations.APIKey(
            user_id=user.user_id,
            key_name=f"{user.first_name}'s API Key",
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=["assets:read", "compliance:read", "reports:read"],
            active=True,
            expires_at=datetime.utcnow() + timedelta(days=90),
            rate_limit_per_hour=1000,
            usage_count=random.randint(100, 5000),
            last_used_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        api_keys.append(api_key)

    db.add_all(api_keys)
    db.commit()
    print(f"  ✓ Created {len(api_keys)} API keys\n")

    # =========================================================================
    # SCHEMA REGISTRY - Features 11 & 12 (Event Catalog + Schema Registry)
    # =========================================================================
    print("📋 Seeding Schema Registry & Event Catalog...")
    db.query(models_advanced.SchemaRegistry).delete()

    schemas = [
        # Event schemas (Feature 11 - Event Catalog)
        models_advanced.SchemaRegistry(
            subject="asset-created-event",
            schema_format=models_advanced.SchemaFormat.JSON_SCHEMA,
            version=1,
            schema_definition={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "integer"},
                    "asset_name": {"type": "string"},
                    "created_by": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["asset_id", "asset_name", "timestamp"]
            },
            compatibility_mode=models_advanced.SchemaCompatibility.BACKWARD,
            is_active=True,
            is_latest=True,
            description="Asset creation event schema",
            asset_id=assets[0].asset_id if assets else None,
            domain_id=domains[0].domain_id if domains else None,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=60)
        ),
        models_advanced.SchemaRegistry(
            subject="compliance-violation-event",
            schema_format=models_advanced.SchemaFormat.JSON_SCHEMA,
            version=1,
            schema_definition={
                "type": "object",
                "properties": {
                    "violation_id": {"type": "integer"},
                    "asset_id": {"type": "integer"},
                    "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                    "description": {"type": "string"}
                },
                "required": ["violation_id", "asset_id", "severity"]
            },
            compatibility_mode=models_advanced.SchemaCompatibility.FULL,
            is_active=True,
            is_latest=True,
            description="Compliance violation detected event",
            domain_id=domains[0].domain_id if domains else None,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=45)
        ),
        models_advanced.SchemaRegistry(
            subject="sla-breach-event",
            schema_format=models_advanced.SchemaFormat.AVRO,
            version=1,
            schema_definition={
                "type": "record",
                "name": "SLABreach",
                "namespace": "com.enterprise.events",
                "fields": [
                    {"name": "metric_id", "type": "int"},
                    {"name": "vendor_id", "type": "int"},
                    {"name": "severity", "type": "string"},
                    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"}
                ]
            },
            compatibility_mode=models_advanced.SchemaCompatibility.BACKWARD,
            is_active=True,
            is_latest=True,
            description="SLA breach notification event",
            domain_id=domains[0].domain_id if domains else None,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        # Data schemas (Feature 12 - Schema Registry)
        models_advanced.SchemaRegistry(
            subject="hr-employee-data",
            schema_format=models_advanced.SchemaFormat.JSON_SCHEMA,
            version=2,
            schema_definition={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "department": {"type": "string"},
                    "hire_date": {"type": "string", "format": "date"}
                },
                "required": ["employee_id", "email"]
            },
            compatibility_mode=models_advanced.SchemaCompatibility.BACKWARD,
            is_active=True,
            is_latest=True,
            description="Employee master data schema (v2 - added department field)",
            asset_id=assets[0].asset_id if assets else None,
            domain_id=domains[0].domain_id if domains else None,
            created_by=users[0].user_id,
            changelog="v2: Added department field for better organization tracking",
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
        models_advanced.SchemaRegistry(
            subject="financial-transaction",
            schema_format=models_advanced.SchemaFormat.AVRO,
            version=1,
            schema_definition={
                "type": "record",
                "name": "Transaction",
                "namespace": "com.enterprise.finance",
                "fields": [
                    {"name": "transaction_id", "type": "string"},
                    {"name": "amount", "type": "double"},
                    {"name": "currency", "type": "string", "default": "USD"},
                    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"}
                ]
            },
            compatibility_mode=models_advanced.SchemaCompatibility.FULL,
            is_active=True,
            is_latest=True,
            description="Financial transaction event schema",
            domain_id=domains[1].domain_id if len(domains) > 1 else domains[0].domain_id,
            created_by=users[0].user_id,
            created_at=datetime.utcnow() - timedelta(days=90)
        ),
    ]
    db.add_all(schemas)
    db.commit()
    print(f"  ✓ Created {len(schemas)} schemas (events + data structures)\n")

    # =========================================================================
    # DATA LINEAGE - Feature 6
    # =========================================================================
    print("🔗 Seeding Data Lineage...")
    db.query(models_advanced.DataLineageEdge).delete()
    db.query(models_advanced.DataLineageNode).delete()

    nodes = [
        models_advanced.DataLineageNode(
            node_type=models_advanced.LineageNodeType.SOURCE,
            node_name="Workday HR System",
            description="Source for employee data",
            location="api://workday.com/employees",
            owner_id=users[0].user_id if users else None,
            domain_id=domains[0].domain_id if domains else None
        ),
        models_advanced.DataLineageNode(
            node_type=models_advanced.LineageNodeType.TABLE,
            node_name="HR Data Warehouse",
            asset_id=assets[0].asset_id,
            description="Centralized employee repository",
            location="snowflake://db.schema.hr_employees",
            owner_id=users[0].user_id if users else None,
            domain_id=domains[0].domain_id if domains else None
        ),
        models_advanced.DataLineageNode(
            node_type=models_advanced.LineageNodeType.ANALYTICS,
            node_name="Tableau Dashboard",
            description="Executive KPI dashboard",
            location="tableau://dashboards/executive",
            owner_id=users[0].user_id if users else None
        ),
    ]
    db.add_all(nodes)
    db.commit()

    edges = [
        models_advanced.DataLineageEdge(
            source_node_id=1,
            target_node_id=2,
            transformation_type=models_advanced.TransformationType.EXTRACT,
            transformation_logic="SELECT * FROM workday.employees",
            transformation_tool="Airflow",
            schedule="daily",
            created_by=users[0].user_id if users else None
        ),
        models_advanced.DataLineageEdge(
            source_node_id=2,
            target_node_id=3,
            transformation_type=models_advanced.TransformationType.AGGREGATE,
            transformation_logic="Group by department, calculate KPIs",
            transformation_tool="dbt",
            schedule="hourly",
            created_by=users[0].user_id if users else None
        ),
    ]
    db.add_all(edges)
    db.commit()
    print(f"  ✓ Created {len(nodes)} lineage nodes and {len(edges)} edges\n")

    # =========================================================================
    # DATA QUALITY RULES - Feature 5
    # =========================================================================
    print("✅ Seeding Data Quality Rules...")
    db.query(models_advanced.QualityCheckRun).delete()
    db.query(models_advanced.DataQualityRule).delete()

    rules = [
        models_advanced.DataQualityRule(
            rule_name="Null Check - Employee ID",
            asset_id=assets[0].asset_id,
            quality_dimension=models_advanced.QualityDimension.COMPLETENESS,
            rule_type="sql",
            rule_definition="SELECT COUNT(*) FROM employees WHERE employee_id IS NULL",
            threshold_value=0.0,
            threshold_operator="<=",
            severity=models_advanced.QualityRuleSeverity.CRITICAL,
            is_active=True,
            schedule="daily",
            created_by=users[0].user_id if users else None
        ),
        models_advanced.DataQualityRule(
            rule_name="Email Format Validation",
            asset_id=assets[0].asset_id,
            quality_dimension=models_advanced.QualityDimension.VALIDITY,
            rule_type="regex",
            rule_definition="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            threshold_value=99.5,
            threshold_operator=">=",
            severity=models_advanced.QualityRuleSeverity.HIGH,
            is_active=True,
            schedule="daily",
            created_by=users[0].user_id if users else None
        ),
        models_advanced.DataQualityRule(
            rule_name="Duplicate Detection",
            asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
            quality_dimension=models_advanced.QualityDimension.UNIQUENESS,
            rule_type="sql",
            rule_definition="SELECT transaction_id, COUNT(*) as cnt FROM transactions GROUP BY transaction_id HAVING cnt > 1",
            threshold_value=0.0,
            threshold_operator="<=",
            severity=models_advanced.QualityRuleSeverity.CRITICAL,
            is_active=True,
            schedule="hourly",
            created_by=users[0].user_id if users else None
        ),
    ]
    db.add_all(rules)
    db.commit()

    # Quality check runs
    check_runs = []
    for rule in rules:
        for i in range(random.randint(10, 30)):
            passed = random.random() > 0.15
            check_run = models_advanced.QualityCheckRun(
                rule_id=rule.rule_id,
                started_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) + timedelta(seconds=random.randint(10, 120)),
                execution_time_seconds=random.uniform(5.0, 120.0),
                passed=passed,
                actual_value=random.uniform(98.0, 100.0) if passed else random.uniform(85.0, 97.9),
                threshold_value=rule.threshold_value,
                total_count=random.randint(10000, 1000000),
                violation_count=random.randint(0, 100) if passed else random.randint(100, 5000)
            )
            check_runs.append(check_run)

    db.add_all(check_runs)
    db.commit()
    print(f"  ✓ Created {len(rules)} quality rules with {len(check_runs)} check runs\n")

    # =========================================================================
    # GOVERNANCE POLICIES - Feature 8
    # =========================================================================
    print("🛡️ Seeding Governance Policies...")
    db.query(models_advanced.PolicyValidation).delete()
    db.query(models_advanced.GovernancePolicy).delete()

    policies = [
        models_advanced.GovernancePolicy(
            policy_name="Naming Convention Enforcement",
            policy_type=models_advanced.PolicyType.NAMING_CONVENTION,
            description="All assets must follow ENV-DOMAIN-SYSTEM-VERSION format",
            policy_definition={
                "pattern": "^(DEV|QA|UAT|PROD)-(HR|FIN|OPS|SALES|IT|DATA)-[A-Z0-9]{2,10}-v\\d+(\\.\\d+)?$"
            },
            is_blocking=True,
            enforcement_level="error",
            is_active=True,
            created_by=users[0].user_id if users else None
        ),
        models_advanced.GovernancePolicy(
            policy_name="Documentation Required",
            policy_type=models_advanced.PolicyType.DOCUMENTATION,
            description="Production assets must have documentation",
            policy_definition={
                "required_fields": ["description", "documentation_url"],
                "min_description_length": 20
            },
            is_blocking=False,
            enforcement_level="warning",
            is_active=True,
            created_by=users[0].user_id if users else None
        ),
    ]
    db.add_all(policies)
    db.commit()

    # Policy validations
    validations = []
    for i in range(30):
        policy = random.choice(policies)
        asset = random.choice(assets)
        passed = random.random() > 0.3
        validation = models_advanced.PolicyValidation(
            policy_id=policy.policy_id,
            asset_id=asset.asset_id,
            asset_name=asset.asset_name,
            passed=passed,
            violations=[{"field": "asset_name", "message": "Does not match pattern"}] if not passed else [],
            validated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
        )
        validations.append(validation)

    db.add_all(validations)
    db.commit()
    print(f"  ✓ Created {len(policies)} policies with {len(validations)} validations\n")

    # =========================================================================
    # IMPACT ANALYSIS - Feature 4
    # =========================================================================
    print("🎯 Seeding Impact Analysis...")
    db.query(models_advanced.ImpactAnalysisRun).delete()

    analyses = []
    for i in range(15):
        asset = random.choice(assets)
        analysis = models_advanced.ImpactAnalysisRun(
            asset_id=asset.asset_id,
            change_type=random.choice(["schema_change", "deprecation", "deletion", "policy_change"]),
            change_description=f"Proposed change to {asset.asset_name}",
            impact_score=random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            downstream_dependencies_count=random.randint(0, 15),
            affected_users_count=random.randint(5, 500),
            migration_required=random.random() > 0.5,
            estimated_migration_hours=random.uniform(2.0, 80.0),
            recommended_actions=["Review dependencies", "Update documentation", "Notify stakeholders"],
            analyzed_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            analyzed_by=users[0].user_id if users else None
        )
        analyses.append(analysis)

    db.add_all(analyses)
    db.commit()
    print(f"  ✓ Created {len(analyses)} impact analyses\n")

    # =========================================================================
    # INTEGRATION LOGS - Feature 13
    # =========================================================================
    print("📝 Seeding Integration Logs...")
    db.query(models_integrations.IntegrationLog).delete()

    int_logs = []
    integration_types = ["servicenow", "jira", "slack", "teams", "webhook"]
    operations = ["sync_asset", "create_ticket", "send_message", "update_status"]

    for i in range(50):
        int_log = models_integrations.IntegrationLog(
            integration_type=random.choice(integration_types),
            operation=random.choice(operations),
            asset_id=random.choice(assets).asset_id if random.random() > 0.3 else None,
            user_id=random.choice(users).user_id if random.random() > 0.5 else None,
            request_payload={"action": "sync", "timestamp": str(datetime.utcnow())},
            response_data={"status": "success", "id": random.randint(1000, 9999)},
            status="success" if random.random() > 0.1 else "failed",
            error_message=None if random.random() > 0.1 else "Connection timeout",
            duration_ms=random.randint(100, 5000),
            external_id=f"EXT-{random.randint(10000, 99999)}",
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
        )
        int_logs.append(int_log)

    db.add_all(int_logs)
    db.commit()
    print(f"  ✓ Created {len(int_logs)} integration logs\n")

    # =========================================================================
    # IMPORT JOBS - Feature 14
    # =========================================================================
    print("📥 Seeding Bulk Import Jobs...")
    db.query(models_integrations.ImportJob).delete()

    jobs = []
    for i in range(10):
        status = random.choice(["completed", "completed", "completed", "failed", "processing"])
        total = random.randint(50, 500)
        successful = total if status == "completed" else random.randint(int(total * 0.7), total - 1)

        job = models_integrations.ImportJob(
            job_name=f"Asset Import {i+1}",
            file_name=f"assets_batch_{i+1}.csv",
            file_size_bytes=random.randint(10000, 500000),
            import_type="assets",
            status=status,
            total_rows=total,
            processed_rows=successful + (total - successful) if status != "processing" else random.randint(0, total),
            successful_rows=successful,
            failed_rows=total - successful,
            validation_errors=[] if status == "completed" else [{"row": random.randint(1, 100), "error": "Invalid format"}],
            created_by=random.choice(users).user_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            started_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if status in ["completed", "failed"] else None
        )
        jobs.append(job)

    db.add_all(jobs)
    db.commit()
    print(f"  ✓ Created {len(jobs)} import jobs\n")

    print("="*70)
    print("  ✅ ALL ADVANCED FEATURES POPULATED SUCCESSFULLY!")
    print("="*70)
    print("\n📊 Summary:")
    print(f"   • {len(webhooks)} Webhooks with {len(deliveries)} deliveries")
    print(f"   • {len(api_keys)} API Keys")
    print(f"   • {len(schemas)} Schema Registry entries (events + data)")
    print(f"   • {len(nodes)} Lineage Nodes with {len(edges)} edges")
    print(f"   • {len(rules)} Quality Rules with {len(check_runs)} check runs")
    print(f"   • {len(policies)} Policies with {len(validations)} validations")
    print(f"   • {len(analyses)} Impact Analyses")
    print(f"   • {len(int_logs)} Integration Logs")
    print(f"   • {len(jobs)} Import Jobs")
    print("="*70 + "\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
