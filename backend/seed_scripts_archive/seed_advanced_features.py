"""
Seed Advanced Features Data
Populates database with comprehensive sample data for all Phase 3 features
"""
from app.database import SessionLocal
from app import models, models_extended, models_advanced, models_integrations
from datetime import datetime, timedelta, date
import random
import secrets
import hashlib
import json

def seed_advanced_features():
    """Seed all advanced feature data"""

    db = SessionLocal()

    try:
        print("\n" + "="*70)
        print("  🚀 SEEDING ADVANCED FEATURES DATA")
        print("="*70 + "\n")

        # Get existing users and assets for foreign key relationships
        users = db.query(models.User).all()
        assets = db.query(models.Asset).all()
        vendors = db.query(models_extended.Vendor).all()

        if not users or not assets:
            print("❌ Error: Base data not found. Please run seed_data.py first!")
            return

        # =====================================================================
        # 1. SLA MONITORING DATA
        # =====================================================================
        print("📊 Seeding SLA Monitoring data...")

        sla_metrics = [
            # AWS SLA Metrics
            models_advanced.SLAMonitoring(
                metric_name="AWS S3 Availability",
                metric_type=models_advanced.SLAMetricType.AVAILABILITY,
                vendor_id=vendors[0].vendor_id if vendors else None,
                asset_id=assets[0].asset_id,
                target_value=99.95,
                target_unit="percentage",
                current_value=99.98,
                is_within_sla=True,
                deviation_percentage=0.03,
                metric_source="cloudwatch",
                collection_method="api",
                measurement_timestamp=datetime.utcnow() - timedelta(minutes=5)
            ),
            models_advanced.SLAMonitoring(
                metric_name="API Response Time",
                metric_type=models_advanced.SLAMetricType.PERFORMANCE,
                asset_id=assets[2].asset_id if len(assets) > 2 else assets[0].asset_id,
                target_value=200.0,
                target_unit="milliseconds",
                current_value=185.3,
                is_within_sla=True,
                deviation_percentage=-7.35,
                metric_source="prometheus",
                collection_method="scrape",
                measurement_timestamp=datetime.utcnow() - timedelta(minutes=2)
            ),
            models_advanced.SLAMonitoring(
                metric_name="Data Freshness",
                metric_type=models_advanced.SLAMetricType.FRESHNESS,
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                target_value=15.0,
                target_unit="minutes",
                current_value=12.5,
                is_within_sla=True,
                deviation_percentage=-16.67,
                metric_source="manual",
                collection_method="query",
                measurement_timestamp=datetime.utcnow() - timedelta(minutes=10)
            ),
            models_advanced.SLAMonitoring(
                metric_name="Database CPU Utilization",
                metric_type=models_advanced.SLAMetricType.CAPACITY,
                vendor_id=vendors[1].vendor_id if len(vendors) > 1 else None,
                asset_id=assets[0].asset_id,
                target_value=80.0,
                target_unit="percentage",
                current_value=92.5,
                is_within_sla=False,
                deviation_percentage=15.63,
                metric_source="cloudwatch",
                collection_method="api",
                measurement_timestamp=datetime.utcnow() - timedelta(minutes=1)
            ),
            models_advanced.SLAMonitoring(
                metric_name="ETL Job Success Rate",
                metric_type=models_advanced.SLAMetricType.RELIABILITY,
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                target_value=99.5,
                target_unit="percentage",
                current_value=98.2,
                is_within_sla=False,
                deviation_percentage=-1.31,
                metric_source="manual",
                collection_method="query",
                measurement_timestamp=datetime.utcnow() - timedelta(hours=1)
            ),
        ]
        db.add_all(sla_metrics)
        db.commit()

        # Create SLA Violations
        violations = [
            models_advanced.SLAViolation(
                metric_id=4,  # Database CPU
                violated_at=datetime.utcnow() - timedelta(hours=2),
                actual_value=92.5,
                target_value=80.0,
                severity="HIGH",
                impact_description="CPU utilization exceeded threshold",
                root_cause="Unexpected query workload spike from analytics users",
                remediation_actions="Scaled up warehouse size, optimized slow queries",
                resolved_at=datetime.utcnow() - timedelta(minutes=30),
                duration_minutes=90
            ),
            models_advanced.SLAViolation(
                metric_id=5,  # ETL Success Rate
                violated_at=datetime.utcnow() - timedelta(days=1),
                actual_value=98.2,
                target_value=99.5,
                severity="MEDIUM",
                impact_description="ETL job failure rate above acceptable threshold",
                root_cause="Source system connectivity issues",
                remediation_actions="Added retry logic, implemented circuit breaker pattern",
                resolved_at=datetime.utcnow() - timedelta(hours=18),
                duration_minutes=360
            ),
            models_advanced.SLAViolation(
                metric_id=4,  # Another CPU violation (unresolved)
                violated_at=datetime.utcnow() - timedelta(minutes=45),
                actual_value=94.8,
                target_value=80.0,
                severity="CRITICAL",
                impact_description="Sustained high CPU utilization",
                root_cause=None,
                remediation_actions=None,
                resolved_at=None,
                duration_minutes=None
            ),
        ]
        db.add_all(violations)
        db.commit()
        print(f"  ✓ Created {len(sla_metrics)} SLA metrics and {len(violations)} violations")

        # =====================================================================
        # 2. API KEYS
        # =====================================================================
        print("🔑 Seeding API Keys data...")

        def generate_api_key():
            random_part = secrets.token_urlsafe(30)
            full_key = f"gp_{random_part}"
            key_prefix = full_key[:10]
            key_hash = hashlib.sha256(full_key.encode()).hexdigest()
            return full_key, key_prefix, key_hash

        api_keys_data = []
        for i, user in enumerate(users[:4]):  # Create keys for first 4 users
            _, prefix, key_hash = generate_api_key()
            expires_days = [30, 90, 180, 365][i % 4]
            api_key = models_integrations.APIKey(
                user_id=user.user_id,
                key_name=f"{user.first_name}'s API Key {i+1}",
                key_prefix=prefix,
                key_hash=key_hash,
                scopes=["assets:read", "compliance:read", "reports:read"][:random.randint(1, 3)],
                expires_at=datetime.utcnow() + timedelta(days=expires_days),
                rate_limit_per_hour=random.choice([100, 500, 1000, 5000]),
                active=random.choice([True, True, True, False]),  # 75% active
                usage_count=random.randint(0, 5000),
                last_used_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)) if random.random() > 0.3 else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            api_keys_data.append(api_key)

        # Add one expired key
        _, prefix, key_hash = generate_api_key()
        expired_key = models_integrations.APIKey(
            user_id=users[0].user_id,
            key_name="Expired Test Key",
            key_prefix=prefix,
            key_hash=key_hash,
            scopes=["assets:read"],
            expires_at=datetime.utcnow() - timedelta(days=10),
            rate_limit_per_hour=100,
            active=False,
            usage_count=234,
            last_used_at=datetime.utcnow() - timedelta(days=15),
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        api_keys_data.append(expired_key)

        db.add_all(api_keys_data)
        db.commit()
        print(f"  ✓ Created {len(api_keys_data)} API keys")

        # =====================================================================
        # 3. WEBHOOKS
        # =====================================================================
        print("🪝 Seeding Webhooks data...")

        webhooks = [
            models_integrations.Webhook(
                user_id=users[0].user_id,
                webhook_name="Slack Compliance Alerts",
                url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
                events=["compliance.violation", "compliance.resolved"],
                secret=secrets.token_hex(32),
                active=True,
                description="Send compliance violations to #data-governance Slack channel",
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            models_integrations.Webhook(
                user_id=users[1].user_id,
                webhook_name="PagerDuty SLA Alerts",
                url="https://events.pagerduty.com/integration/abc123/enqueue",
                events=["sla.violation", "sla.breach.critical"],
                secret=secrets.token_hex(32),
                active=True,
                description="Critical SLA breaches trigger PagerDuty incidents",
                created_at=datetime.utcnow() - timedelta(days=45)
            ),
            models_integrations.Webhook(
                user_id=users[0].user_id,
                webhook_name="Asset Change Notifications",
                url="https://api.company.com/webhooks/asset-changes",
                events=["asset.created", "asset.updated", "asset.deleted"],
                secret=secrets.token_hex(32),
                active=True,
                description="Notify downstream systems of asset registry changes",
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            models_integrations.Webhook(
                user_id=users[2].user_id,
                webhook_name="Inactive Test Webhook",
                url="https://example.com/test",
                events=["asset.created"],
                secret=secrets.token_hex(32),
                active=False,
                description="Disabled test webhook",
                created_at=datetime.utcnow() - timedelta(days=90)
            ),
        ]
        db.add_all(webhooks)
        db.commit()

        # Create Webhook Deliveries
        deliveries = []
        for webhook in webhooks[:3]:  # Create deliveries for active webhooks
            for i in range(random.randint(5, 15)):
                success = random.random() > 0.1  # 90% success rate
                delivered_at = datetime.utcnow() - timedelta(hours=random.randint(1, 720))
                delivery = models_integrations.WebhookDelivery(
                    webhook_id=webhook.webhook_id,
                    event_type=random.choice(webhook.events),
                    payload={"asset_id": random.randint(1, 5), "timestamp": str(delivered_at)},
                    status="success" if success else "failed",
                    http_status=200 if success else random.choice([500, 502, 504]),
                    response_body="OK" if success else "Internal Server Error",
                    delivered_at=delivered_at,
                    retry_count=0 if success else random.randint(1, 3),
                    next_retry_at=None if success else datetime.utcnow() + timedelta(minutes=random.randint(5, 30))
                )
                deliveries.append(delivery)

        db.add_all(deliveries)
        db.commit()
        print(f"  ✓ Created {len(webhooks)} webhooks and {len(deliveries)} delivery records")

        # =====================================================================
        # 4. EVENT CATALOG & SCHEMA REGISTRY
        # =====================================================================
        print("📋 Seeding Event Catalog & Schema Registry data...")

        # Note: Using the models from events endpoints instead
        # Event schemas are managed via API, so we'll create minimal sample data
        event_schemas = [
            models_integrations.EventSchema(
                event_name="AssetCreated",
                version=1,
                schema_format="JSON_SCHEMA",
                schema_definition={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "integer"},
                        "asset_name": {"type": "string"},
                        "domain": {"type": "string"},
                        "created_by": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    },
                    "required": ["asset_id", "asset_name", "created_by", "timestamp"]
                },
                compatibility_mode="BACKWARD",
                is_active=True,
                description="Event emitted when a new asset is registered",
                created_by=users[0].user_id,
                created_at=datetime.utcnow() - timedelta(days=90)
            ),
            models_integrations.EventSchema(
                event_name="AssetCreated",
                version=2,
                schema_format="JSON_SCHEMA",
                schema_definition={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "integer"},
                        "asset_name": {"type": "string"},
                        "domain": {"type": "string"},
                        "environment": {"type": "string"},  # NEW FIELD
                        "created_by": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    },
                    "required": ["asset_id", "asset_name", "created_by", "timestamp"]
                },
                compatibility_mode="BACKWARD",
                is_active=True,
                description="Added environment field (backward compatible)",
                created_by=users[0].user_id,
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            models_integrations.EventSchema(
                event_name="ComplianceViolation",
                version=1,
                schema_format="JSON_SCHEMA",
                schema_definition={
                    "type": "object",
                    "properties": {
                        "violation_id": {"type": "integer"},
                        "asset_id": {"type": "integer"},
                        "violation_type": {"type": "string"},
                        "severity": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                        "description": {"type": "string"},
                        "detected_at": {"type": "string", "format": "date-time"}
                    },
                    "required": ["violation_id", "asset_id", "violation_type", "severity"]
                },
                compatibility_mode="FULL",
                is_active=True,
                description="Event for compliance policy violations",
                created_by=users[1].user_id,
                created_at=datetime.utcnow() - timedelta(days=60)
            ),
            models_integrations.EventSchema(
                event_name="SLABreach",
                version=1,
                schema_format="AVRO",
                schema_definition={
                    "type": "record",
                    "name": "SLABreach",
                    "fields": [
                        {"name": "metric_id", "type": "int"},
                        {"name": "metric_name", "type": "string"},
                        {"name": "target_value", "type": "double"},
                        {"name": "actual_value", "type": "double"},
                        {"name": "severity", "type": "string"},
                        {"name": "timestamp", "type": "long"}
                    ]
                },
                compatibility_mode="BACKWARD",
                is_active=True,
                description="Critical SLA breach notifications (AVRO format)",
                created_by=users[1].user_id,
                created_at=datetime.utcnow() - timedelta(days=45)
            ),
            models_integrations.EventSchema(
                event_name="DataQualityAlert",
                version=1,
                schema_format="JSON_SCHEMA",
                schema_definition={
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "integer"},
                        "asset_id": {"type": "integer"},
                        "check_type": {"type": "string"},
                        "passed": {"type": "boolean"},
                        "failure_count": {"type": "integer"},
                        "details": {"type": "object"}
                    }
                },
                compatibility_mode="FORWARD",
                is_active=True,
                description="Data quality check failure alerts",
                created_by=users[0].user_id,
                created_at=datetime.utcnow() - timedelta(days=20)
            ),
            models_integrations.EventSchema(
                event_name="AssetDeprecated",
                version=1,
                schema_format="JSON_SCHEMA",
                schema_definition={
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "integer"},
                        "reason": {"type": "string"},
                        "deprecated_at": {"type": "string", "format": "date-time"}
                    }
                },
                compatibility_mode="NONE",
                is_active=False,
                description="DEPRECATED: Use lifecycle.changed event instead",
                created_by=users[0].user_id,
                created_at=datetime.utcnow() - timedelta(days=180),
                deprecated_at=datetime.utcnow() - timedelta(days=90)
            ),
        ]
        db.add_all(event_schemas)
        db.commit()
        print(f"  ✓ Created {len(event_schemas)} event schemas (6 events, multiple versions)")

        # =====================================================================
        # 5. POLICY ENFORCEMENT
        # =====================================================================
        print("🛡️ Seeding Policy Enforcement data...")

        policies = [
            models_advanced.GovernancePolicy(
                policy_name="Naming Convention Enforcement",
                policy_type="NAMING",
                policy_definition={
                    "pattern": "^(DEV|QA|UAT|PROD)-(HR|FIN|OPS|SALES|IT|DATA)-[A-Z0-9]{2,10}-v\\d+(\\.\\d+)?$",
                    "description": "ENV-DOMAIN-SYSTEM-VERSION format required"
                },
                severity="HIGH",
                enforcement_level="BLOCKING",
                auto_remediation=False,
                enabled=True,
                applies_to="assets",
                description="All assets must follow standardized naming convention",
                created_by=users[1].user_id
            ),
            models_advanced.GovernancePolicy(
                policy_name="Documentation Required",
                policy_type="DOCUMENTATION",
                policy_definition={
                    "required_fields": ["description", "business_justification", "documentation_url"],
                    "min_description_length": 20
                },
                severity="MEDIUM",
                enforcement_level="WARNING",
                auto_remediation=False,
                enabled=True,
                applies_to="assets",
                description="Production assets must have complete documentation",
                created_by=users[1].user_id
            ),
            models_advanced.GovernancePolicy(
                policy_name="Schema Compatibility Check",
                policy_type="SCHEMA",
                policy_definition={
                    "compatibility_mode": "BACKWARD",
                    "check_breaking_changes": True
                },
                severity="CRITICAL",
                enforcement_level="BLOCKING",
                auto_remediation=False,
                enabled=True,
                applies_to="events",
                description="Event schema changes must maintain backward compatibility",
                created_by=users[0].user_id
            ),
            models_advanced.GovernancePolicy(
                policy_name="Data Freshness SLA",
                policy_type="SLA",
                policy_definition={
                    "max_data_lag_minutes": 30,
                    "applies_to_environments": ["PROD"]
                },
                severity="HIGH",
                enforcement_level="MONITORING",
                auto_remediation=False,
                enabled=True,
                applies_to="assets",
                description="Production data must be refreshed within 30 minutes",
                created_by=users[1].user_id
            ),
            models_advanced.GovernancePolicy(
                policy_name="Automated Security Scan",
                policy_type="SECURITY",
                policy_definition={
                    "scan_on_deploy": True,
                    "block_critical_vulnerabilities": True,
                    "allowed_risk_level": "medium"
                },
                severity="CRITICAL",
                enforcement_level="BLOCKING",
                auto_remediation=False,
                enabled=True,
                applies_to="pipelines",
                description="All deployments must pass security vulnerability scan",
                created_by=users[0].user_id
            ),
        ]
        db.add_all(policies)
        db.commit()

        # Create Policy Validations
        validations = []
        for i in range(20):
            policy = random.choice(policies)
            asset = random.choice(assets)
            passed = random.random() > 0.25  # 75% pass rate

            validation = models_advanced.PolicyValidation(
                policy_id=policy.policy_id,
                asset_id=asset.asset_id,
                validated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
                passed=passed,
                validation_result={
                    "passed": passed,
                    "violations": [] if passed else [
                        {"field": "asset_name", "issue": "Does not match required pattern"},
                        {"field": "documentation", "issue": "Missing required fields"}
                    ][:random.randint(1, 2)],
                    "score": random.randint(70, 100) if passed else random.randint(30, 69)
                },
                validated_by=random.choice(users).user_id
            )
            validations.append(validation)

        db.add_all(validations)
        db.commit()
        print(f"  ✓ Created {len(policies)} governance policies and {len(validations)} validation records")

        # =====================================================================
        # 6. DATA QUALITY
        # =====================================================================
        print("✅ Seeding Data Quality data...")

        quality_rules = [
            models_advanced.DataQualityRule(
                rule_name="Null Check - Critical Fields",
                asset_id=assets[0].asset_id,
                rule_type="COMPLETENESS",
                check_type="NULL_CHECK",
                rule_definition={"columns": ["employee_id", "email", "department"], "threshold": 0},
                threshold_value=0.0,
                severity="CRITICAL",
                enabled=True,
                schedule="daily",
                description="Critical employee fields must not contain nulls"
            ),
            models_advanced.DataQualityRule(
                rule_name="Email Format Validation",
                asset_id=assets[0].asset_id,
                rule_type="VALIDITY",
                check_type="FORMAT_CHECK",
                rule_definition={
                    "column": "email",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                },
                threshold_value=99.5,
                severity="HIGH",
                enabled=True,
                schedule="daily",
                description="Email addresses must be valid format"
            ),
            models_advanced.DataQualityRule(
                rule_name="Duplicate Transaction Detection",
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                rule_type="UNIQUENESS",
                check_type="DUPLICATE_CHECK",
                rule_definition={"columns": ["transaction_id"], "threshold": 0},
                threshold_value=0.0,
                severity="CRITICAL",
                enabled=True,
                schedule="hourly",
                description="Transaction IDs must be unique"
            ),
            models_advanced.DataQualityRule(
                rule_name="Referential Integrity - Orders",
                asset_id=assets[2].asset_id if len(assets) > 2 else assets[0].asset_id,
                rule_type="CONSISTENCY",
                check_type="REFERENTIAL_INTEGRITY",
                rule_definition={
                    "parent_table": "customers",
                    "child_table": "orders",
                    "foreign_key": "customer_id"
                },
                threshold_value=100.0,
                severity="HIGH",
                enabled=True,
                schedule="daily",
                description="All orders must reference valid customers"
            ),
            models_advanced.DataQualityRule(
                rule_name="Anomaly Detection - Revenue",
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                rule_type="ANOMALY",
                check_type="STATISTICAL_ANOMALY",
                rule_definition={
                    "column": "daily_revenue",
                    "method": "z_score",
                    "threshold": 3.0
                },
                threshold_value=3.0,
                severity="MEDIUM",
                enabled=True,
                schedule="daily",
                description="Detect unusual revenue patterns"
            ),
        ]
        db.add_all(quality_rules)
        db.commit()

        # Create Quality Check Results
        check_results = []
        for rule in quality_rules:
            for i in range(random.randint(7, 30)):  # 1-4 weeks of daily checks
                passed = random.random() > 0.15  # 85% pass rate
                check_result = models_advanced.DataQualityCheck(
                    rule_id=rule.rule_id,
                    executed_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    passed=passed,
                    records_checked=random.randint(10000, 1000000),
                    records_passed=random.randint(9500, 10000) if passed else random.randint(7000, 9499),
                    records_failed=random.randint(0, 500) if passed else random.randint(501, 3000),
                    pass_rate=random.uniform(99.5, 100.0) if passed else random.uniform(70.0, 99.4),
                    details={
                        "execution_time_seconds": random.uniform(0.5, 30.0),
                        "sample_failures": [] if passed else [
                            {"row_id": random.randint(1, 10000), "issue": "Invalid format"}
                            for _ in range(min(3, random.randint(1, 5)))
                        ]
                    }
                )
                check_results.append(check_result)

        db.add_all(check_results)
        db.commit()
        print(f"  ✓ Created {len(quality_rules)} data quality rules and {len(check_results)} check results")

        # =====================================================================
        # 7. DATA LINEAGE
        # =====================================================================
        print("🔗 Seeding Data Lineage data...")

        lineage_nodes = [
            # Source systems
            models_advanced.DataLineageNode(
                node_type="SOURCE",
                asset_id=None,
                node_name="Workday HR System",
                system_type="SaaS Application",
                description="Source system for employee data",
                created_by=users[0].user_id
            ),
            models_advanced.DataLineageNode(
                node_type="SOURCE",
                asset_id=None,
                node_name="Oracle ERP",
                system_type="Database",
                description="Financial transactions source",
                created_by=users[0].user_id
            ),
            # Data assets
            models_advanced.DataLineageNode(
                node_type="DATASET",
                asset_id=assets[0].asset_id,
                node_name="HR Data Warehouse",
                system_type="Data Warehouse",
                description="Centralized employee data repository",
                created_by=users[0].user_id
            ),
            models_advanced.DataLineageNode(
                node_type="TRANSFORMATION",
                asset_id=assets[1].asset_id if len(assets) > 1 else None,
                node_name="Finance ETL Pipeline",
                system_type="ETL Job",
                description="Daily financial data processing",
                created_by=users[0].user_id
            ),
            models_advanced.DataLineageNode(
                node_type="DATASET",
                asset_id=assets[1].asset_id if len(assets) > 1 else None,
                node_name="Finance Data Mart",
                system_type="Data Warehouse",
                description="Transformed financial data",
                created_by=users[0].user_id
            ),
            # Consumption points
            models_advanced.DataLineageNode(
                node_type="CONSUMPTION",
                asset_id=None,
                node_name="Tableau Executive Dashboard",
                system_type="BI Tool",
                description="Executive KPI dashboards",
                created_by=users[0].user_id
            ),
            models_advanced.DataLineageNode(
                node_type="CONSUMPTION",
                asset_id=None,
                node_name="Python Analytics Notebook",
                system_type="Analysis Tool",
                description="Data science analysis environment",
                created_by=users[0].user_id
            ),
        ]
        db.add_all(lineage_nodes)
        db.commit()

        # Create Lineage Edges
        edges = [
            # Workday -> HR DW
            models_advanced.DataLineageEdge(
                source_node_id=1, target_node_id=3,
                relationship_type="FEEDS",
                transformation_logic="SELECT * FROM workday.employees WHERE active = true",
                created_by=users[0].user_id
            ),
            # Oracle ERP -> Finance ETL
            models_advanced.DataLineageEdge(
                source_node_id=2, target_node_id=4,
                relationship_type="FEEDS",
                transformation_logic="Extract daily transactions, apply currency conversion",
                created_by=users[0].user_id
            ),
            # Finance ETL -> Finance Data Mart
            models_advanced.DataLineageEdge(
                source_node_id=4, target_node_id=5,
                relationship_type="TRANSFORMS",
                transformation_logic="Aggregate to daily summaries, calculate KPIs",
                created_by=users[0].user_id
            ),
            # HR DW -> Tableau
            models_advanced.DataLineageEdge(
                source_node_id=3, target_node_id=6,
                relationship_type="CONSUMED_BY",
                transformation_logic="Live connection for headcount metrics",
                created_by=users[0].user_id
            ),
            # Finance Data Mart -> Tableau
            models_advanced.DataLineageEdge(
                source_node_id=5, target_node_id=6,
                relationship_type="CONSUMED_BY",
                transformation_logic="Extract connection for financial KPIs",
                created_by=users[0].user_id
            ),
            # HR DW -> Python Notebook
            models_advanced.DataLineageEdge(
                source_node_id=3, target_node_id=7,
                relationship_type="CONSUMED_BY",
                transformation_logic="pandas.read_sql for attrition analysis",
                created_by=users[0].user_id
            ),
        ]
        db.add_all(edges)
        db.commit()
        print(f"  ✓ Created {len(lineage_nodes)} lineage nodes and {len(edges)} lineage edges")

        # =====================================================================
        # 8. ADDITIONAL CHANGE REQUESTS
        # =====================================================================
        print("📝 Seeding additional Change Requests...")

        change_requests = [
            models.ChangeRequest(
                title="Upgrade Snowflake Warehouse to XL",
                description="Increase warehouse size to handle growing workload",
                asset_id=assets[0].asset_id,
                change_type="Modify",
                risk_level="Medium",
                impact_assessment="Query performance improvement, increased cost $2K/month",
                rollback_plan="Downgrade to Large warehouse if issues occur",
                requested_by=users[2].user_id,
                approval_status="Pending",
                approver_id=users[1].user_id,
                status="Pending",
                release_version="R2.1"
            ),
            models.ChangeRequest(
                title="Implement Row-Level Security on Finance Tables",
                description="Add RLS policies to restrict data access by department",
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                change_type="Security",
                risk_level="High",
                impact_assessment="Enhanced data security, requires thorough testing",
                rollback_plan="Drop RLS policies, revert to view-based access control",
                requested_by=users[1].user_id,
                approval_status="Approved",
                approver_id=users[0].user_id,
                status="In Progress",
                release_version="R2.3"
            ),
            models.ChangeRequest(
                title="Deprecate Legacy ETL Pipeline",
                description="Retire old Python-based ETL, fully migrate to Airflow DAGs",
                asset_id=assets[1].asset_id if len(assets) > 1 else assets[0].asset_id,
                change_type="Decommission",
                risk_level="Medium",
                impact_assessment="Eliminate technical debt, improve maintainability",
                rollback_plan="Reactivate legacy pipeline if new system fails",
                requested_by=users[2].user_id,
                approval_status="Approved",
                approver_id=users[1].user_id,
                status="Completed",
                release_version="R2.2"
            ),
            models.ChangeRequest(
                title="Add Real-Time Streaming for Sales Data",
                description="Implement Kafka streaming to reduce data latency from 15min to 30sec",
                asset_id=assets[3].asset_id if len(assets) > 3 else assets[0].asset_id,
                change_type="Enhance",
                risk_level="High",
                impact_assessment="Near real-time analytics capability, requires new infrastructure",
                rollback_plan="Fall back to batch processing if streaming fails",
                requested_by=users[2].user_id,
                approval_status="Rejected",
                approver_id=users[1].user_id,
                status="Rejected",
                release_version=None
            ),
        ]
        db.add_all(change_requests)
        db.commit()
        print(f"  ✓ Created {len(change_requests)} additional change requests")

        # =====================================================================
        # 9. AUDIT LOGS
        # =====================================================================
        print("📜 Seeding Audit Logs...")

        actions = [
            ("CREATE", "Asset", "Created new data warehouse asset"),
            ("UPDATE", "Asset", "Updated lifecycle stage to Active"),
            ("DELETE", "Asset", "Soft deleted deprecated asset"),
            ("APPROVE", "ChangeRequest", "Approved change request"),
            ("REJECT", "ChangeRequest", "Rejected change request due to high risk"),
            ("CREATE", "SLAMetric", "Defined new SLA monitoring metric"),
            ("RESOLVE", "SLAViolation", "Resolved SLA breach after remediation"),
            ("CREATE", "Webhook", "Created new webhook for Slack notifications"),
            ("UPDATE", "Policy", "Updated governance policy threshold"),
            ("EXECUTE", "DataQualityCheck", "Executed daily data quality validation"),
        ]

        audit_logs = []
        for i in range(50):
            action, entity, description = random.choice(actions)
            log = models.AuditLog(
                user_id=random.choice(users).user_id,
                action=action,
                entity_type=entity,
                entity_id=random.randint(1, 10),
                old_value=json.dumps({"status": "Draft"}) if action == "UPDATE" else None,
                new_value=json.dumps({"status": "Active"}) if action == "UPDATE" else None,
                ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (compatible; DaaS-Portal/2.0)",
                description=description,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            )
            audit_logs.append(log)

        db.add_all(audit_logs)
        db.commit()
        print(f"  ✓ Created {len(audit_logs)} audit log entries")

        # =====================================================================
        # 10. COMPLIANCE METRICS (Time Series)
        # =====================================================================
        print("📈 Seeding Compliance Metrics time series...")

        compliance_metrics = []
        # Generate daily metrics for past 90 days
        for days_ago in range(90, 0, -1):
            metric_date = datetime.utcnow() - timedelta(days=days_ago)
            metric = models.ComplianceMetric(
                metric_date=metric_date.date(),
                total_assets=random.randint(45, 55),
                compliant_assets=int(random.randint(45, 55) * random.uniform(0.75, 0.95)),
                compliance_rate=random.uniform(75.0, 95.0),
                violations_count=random.randint(2, 15),
                critical_violations=random.randint(0, 3),
                avg_resolution_time_hours=random.uniform(12.0, 72.0)
            )
            compliance_metrics.append(metric)

        db.add_all(compliance_metrics)
        db.commit()
        print(f"  ✓ Created {len(compliance_metrics)} compliance metric data points (90 days)")

        # =====================================================================
        # SUMMARY
        # =====================================================================
        print("\n" + "="*70)
        print("  ✅ ADVANCED FEATURES DATA SEEDED SUCCESSFULLY!")
        print("="*70)
        print("\n  📊 Summary of Created Data:")
        print(f"     • {len(sla_metrics)} SLA Metrics with {len(violations)} Violations")
        print(f"     • {len(api_keys_data)} API Keys (4 active, 1 expired)")
        print(f"     • {len(webhooks)} Webhooks with {len(deliveries)} Delivery Records")
        print(f"     • {len(event_schemas)} Event Schemas (6 event types, multiple versions)")
        print(f"     • {len(policies)} Governance Policies with {len(validations)} Validation Results")
        print(f"     • {len(quality_rules)} Data Quality Rules with {len(check_results)} Check Results")
        print(f"     • {len(lineage_nodes)} Lineage Nodes with {len(edges)} Lineage Edges")
        print(f"     • {len(change_requests)} Additional Change Requests")
        print(f"     • {len(audit_logs)} Audit Log Entries")
        print(f"     • {len(compliance_metrics)} Compliance Metrics (90-day time series)")
        print("\n  🎯 All dashboards now have realistic sample data!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error seeding advanced features: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_advanced_features()
