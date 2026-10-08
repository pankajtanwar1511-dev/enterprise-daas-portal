"""
Complete seed data for ALL Tools with CORRECT field names
Adds 20-50+ records per table with actual database schema field names
"""
from app.database import SessionLocal
from app import models, models_extended, models_advanced, models_integrations, models_collaboration
from datetime import datetime, timedelta, date
import json
import random

def seed_all_tools():
    """Seed all tool tables with sample data"""

    db = SessionLocal()

    try:
        print("\n" + "="*70)
        print("  🚀 SEEDING ALL TOOLS DATA")
        print("="*70 + "\n")

        # ========================================
        # 1. DATA QUALITY RULES (20 rules)
        # ========================================
        print("Adding 20 Data Quality Rules...")

        quality_rules = []
        rule_configs = [
            ("Employee ID Format", 1, "employees", "employee_id", "completeness", "Employee ID must follow EMP-XXXXXX pattern", "critical"),
            ("Email Uniqueness", 1, "employees", "email", "uniqueness", "Email addresses must be unique", "critical"),
            ("Phone Format", 1, "employees", "phone", "accuracy", "Phone must be in E.164 format", "high"),
            ("Department Valid", 1, "employees", "department", "validity", "Department must be valid code", "high"),
            ("Hire Date Valid", 1, "employees", "hire_date", "timeliness", "Hire date cannot be in future", "critical"),

            ("Transaction Amount", 2, "transactions", "amount", "validity", "Amount must be between 0.01 and 1M", "high"),
            ("Currency ISO", 2, "transactions", "currency", "accuracy", "Currency must be 3-letter ISO code", "medium"),
            ("Transaction Date", 2, "transactions", "txn_date", "timeliness", "Transaction date within 90 days", "low"),
            ("Account Number", 2, "accounts", "account_number", "accuracy", "Account number must be 16 digits", "critical"),
            ("Balance Valid", 2, "accounts", "balance", "validity", "Balance cannot be negative", "high"),

            ("Customer Email", 4, "customers", "email", "accuracy", "Email must be valid format", "medium"),
            ("Customer Name", 4, "customers", "name", "completeness", "Name is required", "critical"),
            ("Customer Status", 4, "customers", "status", "validity", "Status must be active/inactive/suspended", "high"),
            ("ZIP Code", 4, "customers", "zip_code", "accuracy", "ZIP must be 5 or 9 digits", "low"),
            ("Customer Age", 4, "customers", "age", "validity", "Age must be 18-120", "medium"),

            ("Asset Name", 1, "assets", "asset_name", "accuracy", "Name must follow naming convention", "critical"),
            ("Asset Owner", 1, "assets", "owner_id", "completeness", "Owner is required", "critical"),
            ("Asset Docs", 1, "assets", "documentation_url", "completeness", "Documentation URL required for prod", "medium"),
            ("Asset Domain", 1, "assets", "domain_id", "validity", "Domain must be valid", "high"),
            ("Asset Lifecycle", 1, "assets", "lifecycle_stage", "validity", "Lifecycle stage must be valid", "high"),
        ]

        # Enum mappings
        dimension_map = {
            "completeness": models_advanced.QualityDimension.COMPLETENESS,
            "accuracy": models_advanced.QualityDimension.ACCURACY,
            "consistency": models_advanced.QualityDimension.CONSISTENCY,
            "timeliness": models_advanced.QualityDimension.TIMELINESS,
            "validity": models_advanced.QualityDimension.VALIDITY,
            "uniqueness": models_advanced.QualityDimension.UNIQUENESS
        }

        severity_map = {
            "info": models_advanced.QualityRuleSeverity.INFO,
            "low": models_advanced.QualityRuleSeverity.LOW,
            "medium": models_advanced.QualityRuleSeverity.MEDIUM,
            "high": models_advanced.QualityRuleSeverity.HIGH,
            "critical": models_advanced.QualityRuleSeverity.CRITICAL
        }

        for rule_name, asset_id, table, column, dimension, desc, severity in rule_configs:
            quality_rules.append(models_advanced.DataQualityRule(
                rule_name=rule_name,
                description=desc,
                asset_id=asset_id,
                table_name=table,
                column_name=column,
                quality_dimension=dimension_map[dimension],
                rule_type="regex",
                rule_definition=f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL",
                threshold_value=95.0,
                threshold_operator=">=",
                severity=severity_map[severity],
                is_active=random.choice([True, True, True, False]),
                schedule="0 2 * * *",
                alert_on_failure=True,
                alert_channels=json.dumps(["email", "slack"]),
                created_by=1
            ))

        db.add_all(quality_rules)
        db.commit()
        print(f"✓ Created {len(quality_rules)} data quality rules")

        # ========================================
        # 2. QUALITY CHECK RUNS (50 runs)
        # ========================================
        print("Adding 50 Quality Check Runs...")

        check_runs = []
        for i in range(50):
            rule_id = random.randint(1, 20)
            total = random.randint(1000, 500000)
            violations = random.randint(0, int(total * 0.05))
            actual_value = ((total - violations) / total) * 100
            passed = actual_value >= 95.0

            check_runs.append(models_advanced.QualityCheckRun(
                rule_id=rule_id,
                started_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                completed_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                execution_time_seconds=round(random.uniform(1.0, 300.0), 2),
                passed=passed,
                actual_value=round(actual_value, 2),
                threshold_value=95.0,
                violation_count=violations,
                total_count=total,
                error_message=None if passed else "Quality threshold not met",
                sample_violations=json.dumps([{"row": i, "value": "invalid"} for i in range(min(violations, 5))]),
                alert_sent=not passed,
                alert_sent_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if not passed else None
            ))

        db.add_all(check_runs)
        db.commit()
        print(f"✓ Created {len(check_runs)} quality check runs")

        # ========================================
        # 3. DATA LINEAGE NODES (40 nodes)
        # ========================================
        print("Adding 40 Data Lineage Nodes...")

        lineage_nodes = []

        # HR nodes
        hr_nodes = [
            ("hr_employee_raw", "table", "Raw employee data from HRIS"),
            ("hr_employee_cleansed", "transformation", "Data cleansing transformation"),
            ("hr_employee_dw", "table", "Clean employee DW table"),
            ("hr_payroll_source", "table", "Payroll system source"),
            ("hr_payroll_transform", "transformation", "Payroll transformation"),
            ("hr_payroll_dw", "table", "Payroll data warehouse"),
            ("hr_employee_api", "api", "Employee REST API"),
            ("employee-updated-event", "event", "Employee update event"),
        ]

        # Node type enum mapping
        node_type_map = {
            "source": models_advanced.LineageNodeType.SOURCE,
            "table": models_advanced.LineageNodeType.TABLE,
            "view": models_advanced.LineageNodeType.VIEW,
            "transformation": models_advanced.LineageNodeType.TRANSFORMATION,
            "analytics": models_advanced.LineageNodeType.ANALYTICS,
            "api": models_advanced.LineageNodeType.API,
            "file": models_advanced.LineageNodeType.FILE,
            "stream": models_advanced.LineageNodeType.STREAM,
            "event": models_advanced.LineageNodeType.STREAM,  # Map event to stream
            "pipeline": models_advanced.LineageNodeType.TRANSFORMATION  # Map pipeline to transformation
        }

        for name, node_type, desc in hr_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=1,
                node_type=node_type_map[node_type],
                node_name=name,
                description=desc,
                location=f"s3://data-lake/hr/{name}/" if node_type == "table" else f"airflow://hr/{name}",
                schema_definition=json.dumps({"columns": ["id", "name", "email"]}),
                row_count=random.randint(1000, 100000) if node_type == "table" else None,
                size_bytes=random.randint(1000000, 100000000) if node_type == "table" else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 48)),
                owner_id=random.randint(1, 3),
                domain_id=1,
                tags=json.dumps([node_type, "hr"])
            ))

        # Finance nodes
        fin_nodes = [
            ("finance_transactions_raw", "table", "Raw transaction data"),
            ("finance_ledger_source", "table", "General ledger source"),
            ("finance_etl_pipeline", "pipeline", "Finance ETL pipeline"),
            ("finance_dw_transactions", "table", "Transaction DW"),
            ("finance_dw_accounts", "table", "Account balances DW"),
            ("finance_reporting_view", "view", "Finance reporting view"),
            ("transaction-posted-event", "event", "Transaction posted event"),
            ("payment-processed-event", "event", "Payment processed event"),
        ]

        for name, node_type, desc in fin_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=2,
                node_type=node_type_map[node_type],
                node_name=name,
                description=desc,
                location=f"snowflake://prod/finance/{name}",
                schema_definition=json.dumps({"columns": ["txn_id", "amount", "currency"]}),
                row_count=random.randint(10000, 1000000) if node_type in ["table", "view"] else None,
                size_bytes=random.randint(10000000, 500000000) if node_type in ["table", "view"] else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 24)),
                owner_id=random.randint(1, 3),
                domain_id=2,
                tags=json.dumps([node_type, "finance"])
            ))

        # Operations nodes
        ops_nodes = [
            ("ops_orders_source", "table", "Order management source"),
            ("ops_inventory_source", "table", "Inventory system source"),
            ("ops_logistics_api", "api", "Logistics data API"),
            ("ops_shipping_events", "event", "Shipping status events"),
            ("ops_warehouse_dw", "table", "Warehouse data warehouse"),
        ]

        for name, node_type, desc in ops_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=3,
                node_type=node_type_map[node_type],
                node_name=name,
                description=desc,
                location=f"postgres://ops/{name}",
                schema_definition=json.dumps({"columns": ["order_id", "status"]}),
                row_count=random.randint(5000, 50000) if node_type == "table" else None,
                size_bytes=random.randint(5000000, 50000000) if node_type == "table" else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 72)),
                owner_id=random.randint(1, 3),
                domain_id=3,
                tags=json.dumps([node_type, "operations"])
            ))

        # Sales nodes
        sales_nodes = [
            ("sales_crm_contacts", "table", "CRM contacts data"),
            ("sales_opportunities", "table", "Sales opportunities"),
            ("sales_pipeline_view", "view", "Sales pipeline view"),
            ("deal-closed-event", "event", "Deal closed event"),
            ("lead-created-event", "event", "New lead created"),
            ("sales_analytics_dw", "table", "Sales analytics warehouse"),
        ]

        for name, node_type, desc in sales_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=4,
                node_type=node_type_map[node_type],
                node_name=name,
                description=desc,
                location=f"salesforce://prod/{name}" if "crm" in name else f"redshift://sales/{name}",
                schema_definition=json.dumps({"columns": ["customer_id", "amount"]}),
                row_count=random.randint(2000, 20000) if node_type in ["table", "view"] else None,
                size_bytes=random.randint(2000000, 20000000) if node_type in ["table", "view"] else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 168)),
                owner_id=random.randint(1, 3),
                domain_id=4,
                tags=json.dumps([node_type, "sales"])
            ))

        # Governance events
        gov_events = [
            ("asset-created-event", "event", "New asset created"),
            ("compliance-violation-event", "event", "Compliance violation detected"),
            ("change-approved-event", "event", "Change request approved"),
            ("sla-breached-event", "event", "SLA breached"),
            ("quality-check-failed-event", "event", "Quality check failed"),
        ]

        for name, node_type, desc in gov_events:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=1,
                node_type=node_type_map[node_type],
                node_name=name,
                description=desc,
                location=f"kafka://events/{name}",
                schema_definition=json.dumps({"event_id": "string", "timestamp": "datetime"}),
                owner_id=1,
                domain_id=6,
                tags=json.dumps(["event", "governance", "kafka"])
            ))

        db.add_all(lineage_nodes)
        db.commit()
        print(f"✓ Created {len(lineage_nodes)} lineage nodes")

        # ========================================
        # 4. DATA LINEAGE EDGES (30 edges)
        # ========================================
        print("Adding 30 Data Lineage Edges...")

        lineage_edges = []
        edge_patterns = [
            (1, 2), (2, 3), (4, 5), (5, 6), (3, 7), (1, 8),  # HR
            (9, 11), (10, 11), (11, 12), (12, 13), (13, 14), (12, 15), (13, 16),  # Finance
            (17, 21), (18, 21), (17, 19), (19, 21), (20, 21),  # Ops
            (22, 24), (23, 24), (24, 26), (22, 27), (23, 28), (24, 25),  # Sales
        ]

        for source_id, target_id in edge_patterns:
            lineage_edges.append(models_advanced.DataLineageEdge(
                source_node_id=source_id,
                target_node_id=target_id,
                transformation_type=models_advanced.TransformationType.TRANSFORM,
                transformation_logic=f"Data flows from node {source_id} to {target_id}",
                transformation_tool="Apache Airflow",
                column_mappings=json.dumps({"source_col": "target_col"}),
                execution_time_seconds=round(random.uniform(10.0, 600.0), 2),
                rows_processed=random.randint(1000, 1000000),
                bytes_processed=random.randint(1000000, 100000000),
                schedule="0 2 * * *",
                last_run=datetime.now() - timedelta(hours=random.randint(1, 48)),
                next_run=datetime.now() + timedelta(hours=random.randint(1, 24)),
                is_active=True,
                created_by=1
            ))

        db.add_all(lineage_edges)
        db.commit()
        print(f"✓ Created {len(lineage_edges)} lineage edges")

        # ========================================
        # 5. SCHEMA REGISTRY (25 schemas)
        # ========================================
        print("Adding 25 Schema Registry entries...")

        schemas = []
        subjects = [
            ("hr-employee", 1, 1, "avro"), ("hr-payroll", 1, 1, "avro"),
            ("finance-transaction", 2, 2, "json"), ("finance-account", 2, 2, "avro"),
            ("finance-payment", 2, 2, "json"),
            ("ops-order", 3, 3, "json"), ("ops-shipment", 3, 3, "avro"),
            ("ops-inventory", 3, 3, "json"),
            ("sales-contact", 4, 4, "avro"), ("sales-opportunity", 4, 4, "json"),
            ("sales-quote", 4, 4, "json"),
            ("asset-created-event", 1, 6, "avro"), ("compliance-violation-event", 1, 6, "avro"),
            ("change-approved-event", 1, 6, "avro"), ("sla-breached-event", 1, 6, "json"),
            ("quality-check-failed-event", 1, 6, "json"),
            ("customer-profile", 4, 4, "json"), ("product-catalog", 3, 3, "avro"),
            ("user-activity", 1, 6, "json"), ("audit-log", 1, 6, "avro"),
            ("notification-message", 1, 6, "json"), ("task-assignment", 1, 6, "json"),
            ("comment-thread", 1, 6, "json"), ("webhook-payload", 1, 6, "json"),
            ("api-request-log", 1, 6, "json"),
        ]

        # Schema format enum mapping
        schema_format_map = {
            "avro": models_advanced.SchemaFormat.AVRO,
            "json": models_advanced.SchemaFormat.JSON_SCHEMA,
            "json_schema": models_advanced.SchemaFormat.JSON_SCHEMA,
            "protobuf": models_advanced.SchemaFormat.PROTOBUF,
            "parquet": models_advanced.SchemaFormat.PARQUET,
            "sql_ddl": models_advanced.SchemaFormat.SQL_DDL
        }

        for subject, asset_id, domain_id, format_type in subjects:
            version = random.randint(1, 5)
            schemas.append(models_advanced.SchemaRegistry(
                subject=subject,
                schema_format=schema_format_map[format_type],
                version=version,
                schema_definition=json.dumps({"type": "record", "name": subject.replace("-", "_"), "fields": [{"name": "id", "type": "string"}]}),
                compatibility_mode=models_advanced.SchemaCompatibility.BACKWARD,
                is_active=True,
                is_latest=True,
                asset_id=asset_id,
                domain_id=domain_id,
                created_by=1,
                description=f"Schema for {subject} data",
                changelog=f"v{version}: Latest version",
                examples=json.dumps([{"id": "123", "name": "example"}])
            ))

        db.add_all(schemas)
        db.commit()
        print(f"✓ Created {len(schemas)} schema registry entries")

        # ========================================
        # 6. SLA MONITORING (60 records)
        # ========================================
        print("Adding 60 SLA Monitoring records...")

        sla_records = []

        # SLA metric type enum mapping
        sla_metric_type_map = {
            "availability": models_advanced.SLAMetricType.AVAILABILITY,
            "performance": models_advanced.SLAMetricType.PERFORMANCE,
            "reliability": models_advanced.SLAMetricType.RELIABILITY,
            "freshness": models_advanced.SLAMetricType.FRESHNESS,
            "timeliness": models_advanced.SLAMetricType.FRESHNESS,  # Map timeliness to freshness
            "capacity": models_advanced.SLAMetricType.CAPACITY,
            "response_time": models_advanced.SLAMetricType.PERFORMANCE  # Map response_time to performance
        }

        metric_configs = [
            ("availability", "Service Availability", "%", 99.95, 0.1),
            ("performance", "Query Response Time", "seconds", 3.0, 0.5),
            ("performance", "Data Processing Latency", "seconds", 300.0, 30.0),
            ("performance", "Support Response Time", "hours", 4.0, 1.0),
            ("performance", "API Response Time", "milliseconds", 200.0, 50.0),
            ("freshness", "Data Freshness", "minutes", 15.0, 5.0),
        ]

        for _ in range(60):
            metric_type, metric_name, unit, target, variance = random.choice(metric_configs)
            actual = target + random.uniform(-variance, variance)
            is_within = actual >= target if "Rate" not in metric_name else actual <= target
            deviation = ((actual - target) / target) * 100

            sla_records.append(models_advanced.SLAMonitoring(
                vendor_id=random.randint(1, 3),
                asset_id=random.choice([1, 2, 3, 4, None]),
                metric_type=sla_metric_type_map[metric_type],
                metric_name=metric_name,
                target_value=target,
                target_unit=unit,
                current_value=round(actual, 2),
                measurement_timestamp=datetime.now() - timedelta(hours=random.randint(1, 720)),
                is_within_sla=is_within,
                deviation_percentage=round(deviation, 2),
                metric_source="monitoring_system",
                collection_method="automated"
            ))

        db.add_all(sla_records)
        db.commit()
        print(f"✓ Created {len(sla_records)} SLA monitoring records")

        # ========================================
        # 7. WEBHOOKS (15 webhooks)
        # ========================================
        print("Adding 15 Webhooks...")

        webhooks = []
        webhook_configs = [
            ("Slack Governance Alerts", "https://hooks.slack.com/services/T00/B00/XXX", ["compliance.violation", "change.approved", "asset.created"]),
            ("Slack Quality Alerts", "https://hooks.slack.com/services/T00/B01/XXX", ["quality.check.failed", "quality.rule.created"]),
            ("Teams Change Notifications", "https://company.webhook.office.com/webhookb2/xxx1", ["change.requested", "change.approved", "change.rejected"]),
            ("Teams SLA Alerts", "https://company.webhook.office.com/webhookb2/xxx2", ["sla.breached", "sla.warning"]),
            ("ServiceNow Change Integration", "https://company.service-now.com/api/now/table/change_request", ["change.requested", "change.approved"]),
            ("ServiceNow Incident Integration", "https://company.service-now.com/api/now/table/incident", ["compliance.violation", "sla.breached"]),
            ("PagerDuty Critical Alerts", "https://events.pagerduty.com/v2/enqueue", ["sla.critical", "quality.critical"]),
            ("Datadog Metrics", "https://api.datadoghq.com/api/v1/events", ["asset.created", "quality.check.completed"]),
            ("Email Digest", "https://api.sendgrid.com/v3/mail/send", ["asset.created", "change.approved"]),
            ("Jira Issue Creation", "https://company.atlassian.net/rest/api/2/issue", ["compliance.violation", "quality.check.failed"]),
            ("Confluence Doc Update", "https://company.atlassian.net/wiki/rest/api/content", ["asset.created", "schema.registered"]),
            ("AWS EventBridge", "https://events.us-east-1.amazonaws.com/", ["asset.created", "change.approved"]),
            ("Azure Event Grid", "https://eventgrid.azure.net/api/events", ["quality.check.completed"]),
            ("Custom Analytics Platform", "https://analytics.company.com/api/v1/events", ["asset.created"]),
            ("Audit Log Archive", "https://logs.company.com/api/v1/archive", ["audit.log", "change.approved"]),
        ]

        for name, url, events in webhook_configs:
            webhooks.append(models_integrations.Webhook(
                name=name,
                url=url,
                secret=f"webhook_secret_{random.randint(1000, 9999)}",
                events=json.dumps(events),
                active=random.choice([True, True, True, False]),
                created_by=1,
                last_triggered=datetime.now() - timedelta(hours=random.randint(1, 720)),
                retry_count=random.randint(3, 5),
                timeout_seconds=random.randint(30, 90)
            ))

        db.add_all(webhooks)
        db.commit()
        print(f"✓ Created {len(webhooks)} webhooks")

        # ========================================
        # 8. WEBHOOK DELIVERIES (100 logs)
        # ========================================
        print("Adding 100 Webhook Deliveries...")

        deliveries = []
        event_types = [
            "compliance.violation", "change.approved", "asset.created", "quality.check.failed",
            "sla.breached", "schema.registered", "change.requested", "asset.updated"
        ]

        for _ in range(100):
            success = random.choice([True, True, True, False])
            deliveries.append(models_integrations.WebhookDelivery(
                webhook_id=random.randint(1, 15),
                event=random.choice(event_types),
                payload=json.dumps({"event_id": random.randint(1000, 9999), "timestamp": datetime.now().isoformat()}),
                status_code=200 if success else random.choice([500, 503, 504]),
                response_body='{"ok": true}' if success else '{"error": "Internal error"}',
                error_message=None if success else "Delivery failed",
                delivered_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                duration_ms=random.randint(50, 5000),
                attempt_number=1 if success else random.randint(1, 3),
                success=success
            ))

        db.add_all(deliveries)
        db.commit()
        print(f"✓ Created {len(deliveries)} webhook deliveries")

        # ========================================
        # 9. API KEYS (20 keys)
        # ========================================
        print("Adding 20 API Keys...")

        api_keys = []
        key_configs = [
            ("ETL Pipeline Service Account", ["asset:read", "asset:create", "lineage:write"], 90),
            ("Analytics Dashboard", ["asset:read", "compliance:read", "reports:read"], 365),
            ("Monitoring Service", ["sla:read", "quality:read"], 30),
            ("CI/CD Automation", ["asset:create", "asset:update"], 180),
            ("Data Science Platform", ["asset:read", "lineage:read"], 365),
            ("Business Intelligence Tool", ["asset:read", "reports:read"], 365),
            ("External Partner API", ["asset:read"], 90),
            ("Mobile App Backend", ["asset:read"], 180),
            ("Slack Integration Bot", ["asset:read", "notifications:create"], 365),
            ("Tableau Connector", ["asset:read", "schema:read"], 365),
            ("Airflow DAG Runner", ["asset:read", "lineage:write"], 180),
            ("Data Catalog Sync", ["asset:read", "schema:read"], 365),
            ("Compliance Auditor", ["asset:read", "compliance:read"], 180),
            ("Backup Service", ["asset:read"], 365),
            ("Testing Framework", ["asset:read", "asset:create"], 90),
            ("Documentation Generator", ["asset:read", "schema:read"], 365),
            ("Cost Management Tool", ["asset:read", "budget:read"], 180),
            ("Security Scanner", ["asset:read", "compliance:read"], 180),
            ("Performance Monitor", ["asset:read", "sla:read"], 90),
            ("Developer Sandbox", ["asset:read"], 30),
        ]

        for i, (name, scopes, expiry_days) in enumerate(key_configs):
            is_active = random.choice([True, True, True, False])
            api_keys.append(models_integrations.APIKey(
                user_id=random.randint(1, 5),
                key_name=name,
                key_prefix=f"sk_{i+1:03d}",
                key_hash=f"$2b$12${''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=40))}",
                active=is_active,
                scopes=json.dumps(scopes),
                last_used_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if is_active else None,
                expires_at=datetime.now() + timedelta(days=expiry_days),
                usage_count=random.randint(0, 10000) if is_active else 0,
                rate_limit_per_hour=random.randint(100, 1000)
            ))

        db.add_all(api_keys)
        db.commit()
        print(f"✓ Created {len(api_keys)} API keys")

        # ========================================
        # 10. INTEGRATION LOGS (150 logs)
        # ========================================
        print("Adding 150 Integration Logs...")

        integration_logs = []
        integration_types = ["webhook", "api", "sync", "export", "import"]
        operations = ["create", "update", "delete", "read", "sync", "export", "import"]

        for _ in range(150):
            success = random.choice([True, True, True, False])
            integration_logs.append(models_integrations.IntegrationLog(
                integration_type=random.choice(integration_types),
                operation=random.choice(operations),
                asset_id=random.choice([1, 2, 3, 4, None]),
                user_id=random.randint(1, 5),
                request_payload=json.dumps({"request_id": random.randint(10000, 99999)}),
                response_data=json.dumps({"success": True}) if success else json.dumps({"error": "Failed"}),
                status="success" if success else "error",
                error_message=None if success else "Integration error occurred",
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                duration_ms=random.randint(50, 5000),
                external_id=f"ext_{random.randint(1000, 9999)}",
                external_url=f"https://external-system.com/resource/{random.randint(1, 100)}"
            ))

        db.add_all(integration_logs)
        db.commit()
        print(f"✓ Created {len(integration_logs)} integration logs")

        # ========================================
        # 11. TASKS (40 tasks)
        # ========================================
        print("Adding 40 Tasks...")

        tasks = []
        priorities = ["low", "medium", "high", "critical"]
        statuses = ["pending", "in_progress", "completed", "cancelled"]

        # Priority enum mapping
        priority_map = {
            "low": models_collaboration.TaskPriority.LOW,
            "medium": models_collaboration.TaskPriority.MEDIUM,
            "high": models_collaboration.TaskPriority.HIGH,
            "critical": models_collaboration.TaskPriority.CRITICAL
        }

        task_titles = [
            "Review asset naming compliance",
            "Approve change request for production",
            "Update data lineage documentation",
            "Investigate data quality failures",
            "Remediate compliance violation",
            "Document new schema changes",
            "Review SLA breach incidents",
            "Approve vendor contract renewal",
            "Update asset metadata",
            "Complete security audit checklist",
        ]

        for i in range(40):
            status = random.choice(statuses)
            due = date.today() + timedelta(days=random.randint(1, 30))
            priority_str = random.choice(priorities)

            tasks.append(models_collaboration.Task(
                title=random.choice(task_titles),
                description=f"Task description {i+1}: Complete this assigned task.",
                assigned_to=random.randint(1, 5),
                created_by=random.randint(1, 3),
                initiative_id=random.choice([None, 1, 2]),
                priority=priority_map[priority_str],
                status=status,
                due_date=due,
                start_date=date.today() - timedelta(days=random.randint(1, 10)) if status != "pending" else None,
                completed_at=datetime.now() - timedelta(days=random.randint(1, 10)) if status == "completed" else None,
                estimated_hours=random.randint(1, 40),
                actual_hours=random.randint(1, 50) if status == "completed" else None,
                tags="governance,compliance"
            ))

        db.add_all(tasks)
        db.commit()
        print(f"✓ Created {len(tasks)} tasks")

        # ========================================
        # 12. NOTIFICATIONS (60 notifications)
        # ========================================
        print("Adding 60 Notifications...")

        notifications = []
        notif_types = ["info", "warning", "error", "success"]

        titles = {
            "info": ["New asset created", "Schema updated", "Task assigned"],
            "warning": ["SLA approaching threshold", "Upcoming deadline", "Pending approval"],
            "error": ["Quality check failed", "SLA breached", "Compliance violation"],
            "success": ["Change approved", "Quality check passed", "Task completed"]
        }

        for i in range(60):
            notif_type = random.choice(notif_types)
            is_read = random.choice([True, False])
            priority_str = random.choice(priorities)

            notifications.append(models_collaboration.Notification(
                user_id=random.randint(1, 5),
                type=notif_type,
                title=random.choice(titles[notif_type]),
                message=f"Notification message {i+1} with details about the event.",
                link=f"/assets/{random.randint(1, 5)}" if random.choice([True, False]) else None,
                entity_type=random.choice(["asset", "task", "change"]),
                entity_id=random.randint(1, 20),
                read=is_read,
                read_at=datetime.now() - timedelta(hours=random.randint(1, 48)) if is_read else None,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                priority=priority_map[priority_str]
            ))

        db.add_all(notifications)
        db.commit()
        print(f"✓ Created {len(notifications)} notifications")

        # ========================================
        # 13. COMMENTS (80 comments)
        # ========================================
        print("Adding 80 Comments...")

        comments = []
        comment_texts = [
            "This looks good, approved!",
            "Can we schedule this for next week?",
            "I have concerns about downstream impact.",
            "Please update documentation first.",
            "What is the rollback plan?",
            "Has this been tested in QA?",
            "Approved with conditions.",
            "Please coordinate with infrastructure team.",
            "This needs security review first.",
            "Great work! Ready to deploy.",
        ]

        for i in range(80):
            comments.append(models_collaboration.Comment(
                entity_type=random.choice(["asset", "change", "task"]),
                entity_id=random.randint(1, 5),
                user_id=random.randint(1, 5),
                comment_text=random.choice(comment_texts),
                parent_comment_id=random.choice([None, None, random.randint(1, max(1, i-1))]),
                mentioned_users=None,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                edited=False,
                deleted=False
            ))

        db.add_all(comments)
        db.commit()
        print(f"✓ Created {len(comments)} comments")

        # ========================================
        # 14. ACTIVITY LOGS (200 activities)
        # ========================================
        print("Adding 200 Activity Logs...")

        activity_logs = []
        actions = [
            "created", "updated", "deleted",
            "approved", "rejected",
            "executed", "failed",
            "logged_in", "logged_out",
            "assigned", "completed"
        ]

        for _ in range(200):
            activity_logs.append(models_collaboration.ActivityLog(
                user_id=random.randint(1, 5),
                action=random.choice(actions),
                entity_type=random.choice(["asset", "change", "task", "schema"]),
                entity_id=random.randint(1, 20),
                entity_name=f"Entity {random.randint(1, 100)}",
                description=f"User performed action",
                meta_data=json.dumps({"ip": f"192.168.1.{random.randint(1, 255)}", "user_agent": "Mozilla/5.0"}),
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720))
            ))

        db.add_all(activity_logs)
        db.commit()
        print(f"✓ Created {len(activity_logs)} activity logs")

        # ========================================
        # 15. GOVERNANCE POLICIES (15 policies)
        # ========================================
        print("Adding 15 Governance Policies...")

        policies = []
        policy_configs = [
            ("Naming Convention Enforcement", "naming", "All assets must follow naming convention"),
            ("Documentation Requirement", "documentation", "All prod assets must have docs"),
            ("Ownership Assignment Policy", "ownership", "All prod assets must have owners"),
            ("Data Quality Thresholds", "quality", "Quality pass rate must be >= 95%"),
            ("SLA Monitoring", "sla", "Critical services must have SLA monitoring"),
            ("Schema Versioning", "schema", "All schemas must be versioned"),
            ("PII Data Handling", "security", "PII data must be encrypted"),
            ("Data Classification", "classification", "All data must be classified"),
            ("Security Scanning", "security_scan", "All assets must pass security scan"),
            ("Audit Logging", "documentation", "All access must be logged"),
            ("Disaster Recovery", "ownership", "Critical assets must have DR plan"),
            ("Performance Standards", "sla", "API response < 200ms"),
            ("Data Lineage Tracking", "documentation", "All transforms must be documented"),
            ("Cost Optimization", "ownership", "Unused assets must be archived"),
            ("Vendor Management", "ownership", "All vendors must have signed DPA"),
        ]

        # PolicyType enum mapping
        policy_type_map = {
            "naming": models_advanced.PolicyType.NAMING_CONVENTION,
            "documentation": models_advanced.PolicyType.DOCUMENTATION,
            "ownership": models_advanced.PolicyType.OWNERSHIP,
            "classification": models_advanced.PolicyType.DATA_CLASSIFICATION,
            "sla": models_advanced.PolicyType.SLA_REQUIREMENT,
            "security": models_advanced.PolicyType.SECURITY_SCAN,
            "security_scan": models_advanced.PolicyType.SECURITY_SCAN,
            "schema": models_advanced.PolicyType.SCHEMA_VALIDATION,
            "quality": models_advanced.PolicyType.QUALITY_THRESHOLD
        }

        for name, policy_type, desc in policy_configs:
            policies.append(models_advanced.GovernancePolicy(
                policy_name=name,
                policy_type=policy_type_map[policy_type],
                description=desc,
                policy_definition=json.dumps({"rule": f"Policy rule for {name}"}),
                is_blocking=random.choice([True, False]),
                enforcement_level=random.choice(["advisory", "warning", "blocking"]),
                applies_to_domains=json.dumps([1, 2, 3, 4, 5, 6]),
                applies_to_environments=json.dumps(["DEV", "QA", "UAT", "PROD"]),
                exemption_allowed=True,
                exemption_requires_approval=True,
                is_active=True,
                created_by=1
            ))

        db.add_all(policies)
        db.commit()
        print(f"✓ Created {len(policies)} governance policies")

        # ========================================
        # 16. POLICY VALIDATIONS (50 validations)
        # ========================================
        print("Adding 50 Policy Validations...")

        validations = []
        for _ in range(50):
            passed = random.choice([True, True, True, False])
            validations.append(models_advanced.PolicyValidation(
                policy_id=random.randint(1, 15),
                asset_id=random.randint(1, 5),
                asset_name=f"PROD-HR-DW-v{random.randint(1, 5)}",
                pipeline_id=f"pipeline_{random.randint(1, 100)}",
                commit_sha=f"abc{random.randint(100000, 999999)}",
                branch="main",
                triggered_by="jenkins",
                passed=passed,
                violations=json.dumps([]) if passed else json.dumps([{"rule": "violation"}]),
                deployment_blocked=not passed,
                exemption_requested=False,
                exemption_approved=False,
                exemption_approver=None,
                exemption_reason=None,
                validated_at=datetime.now() - timedelta(hours=random.randint(1, 720))
            ))

        db.add_all(validations)
        db.commit()
        print(f"✓ Created {len(validations)} policy validations")

        # ========================================
        # 17. IMPACT ANALYSIS RUNS (30 runs)
        # ========================================
        print("Adding 30 Impact Analysis Runs...")

        impact_runs = []
        for _ in range(30):
            up_count = random.randint(1, 20)
            down_count = random.randint(5, 50)
            impact_runs.append(models_advanced.ImpactAnalysisRun(
                asset_id=random.randint(1, 5),
                change_type="schema_change",
                change_description="Modifying table schema",
                impact_score=random.choice(["low", "medium", "high", "critical"]),
                upstream_dependencies_count=up_count,
                downstream_dependencies_count=down_count,
                affected_assets=json.dumps([f"asset_{i}" for i in range(min(down_count, 10))]),
                affected_pipelines=json.dumps([f"pipeline_{i}" for i in range(random.randint(1, 5))]),
                affected_reports=json.dumps([f"report_{i}" for i in range(random.randint(1, 5))]),
                affected_users_count=random.randint(10, 500),
                affected_teams=json.dumps(["team_a", "team_b"]),
                migration_required=random.choice([True, False]),
                estimated_migration_hours=round(random.uniform(1.0, 40.0), 1),
                recommended_actions=json.dumps(["Update downstream consumers", "Test thoroughly"]),
                rollback_plan="Restore from backup",
                analyzed_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                analyzed_by=random.randint(1, 3),
                analysis_depth=random.randint(1, 5)
            ))

        db.add_all(impact_runs)
        db.commit()
        print(f"✓ Created {len(impact_runs)} impact analysis runs")

        # ========================================
        # 18. IMPORT JOBS (25 jobs)
        # ========================================
        print("Adding 25 Import Jobs...")

        import_jobs = []
        job_statuses = ["pending", "processing", "completed", "failed"]
        import_types = ["asset_import", "schema_import", "lineage_import", "metadata_sync"]

        for i in range(25):
            status = random.choice(job_statuses)
            total = random.randint(10, 500)
            successful = random.randint(0, total) if status in ["completed", "failed"] else 0
            failed = total - successful if status == "failed" else 0

            import_jobs.append(models_integrations.ImportJob(
                job_name=f"Import Job {i+1}",
                file_name=f"import_data_{i+1}.csv",
                file_size_bytes=random.randint(1000, 10000000),
                import_type=random.choice(import_types),
                status=status,
                total_rows=total,
                processed_rows=successful + failed if status != "pending" else 0,
                successful_rows=successful,
                failed_rows=failed,
                validation_errors=json.dumps([{"row": random.randint(1, 100), "error": "Invalid format"}]) if failed > 0 else None,
                created_by=random.randint(1, 3),
                started_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if status != "pending" else None,
                completed_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if status == "completed" else None
            ))

        db.add_all(import_jobs)
        db.commit()
        print(f"✓ Created {len(import_jobs)} import jobs")

        # ========================================
        # 19. SLA VIOLATIONS (30 violations)
        # ========================================
        print("Adding 30 SLA Violations...")

        sla_violations = []
        for _ in range(30):
            target = random.uniform(90.0, 99.99)
            actual = target - random.uniform(0.1, 10.0)
            deviation = ((target - actual) / target) * 100
            duration = random.randint(5, 480)

            sla_violations.append(models_advanced.SLAViolation(
                metric_id=random.randint(1, 60),
                violated_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                resolved_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if random.choice([True, False]) else None,
                duration_minutes=duration,
                target_value=round(target, 2),
                actual_value=round(actual, 2),
                deviation_percentage=round(deviation, 2),
                severity=random.choice(["low", "medium", "high", "critical"]),
                impact_description="Service performance degraded",
                affected_users_count=random.randint(10, 1000),
                alert_sent=True,
                alert_sent_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                incident_created=random.choice([True, False]),
                incident_id=f"INC{random.randint(1000, 9999)}",
                root_cause="High load on database",
                remediation_actions="Scaled up resources"
            ))

        db.add_all(sla_violations)
        db.commit()
        print(f"✓ Created {len(sla_violations)} SLA violations")

        print("\n" + "="*70)
        print("  ✅ ALL TOOLS DATA SEEDED SUCCESSFULLY!")
        print("="*70)
        print(f"\n  📊 Total Records Created:")
        print(f"     • {len(quality_rules)} Data Quality Rules")
        print(f"     • {len(check_runs)} Quality Check Runs")
        print(f"     • {len(lineage_nodes)} Data Lineage Nodes")
        print(f"     • {len(lineage_edges)} Data Lineage Edges")
        print(f"     • {len(schemas)} Schema Registry Entries")
        print(f"     • {len(sla_records)} SLA Monitoring Records")
        print(f"     • {len(webhooks)} Webhooks")
        print(f"     • {len(deliveries)} Webhook Deliveries")
        print(f"     • {len(api_keys)} API Keys")
        print(f"     • {len(integration_logs)} Integration Logs")
        print(f"     • {len(tasks)} Tasks")
        print(f"     • {len(notifications)} Notifications")
        print(f"     • {len(comments)} Comments")
        print(f"     • {len(activity_logs)} Activity Logs")
        print(f"     • {len(policies)} Governance Policies")
        print(f"     • {len(validations)} Policy Validations")
        print(f"     • {len(impact_runs)} Impact Analysis Runs")
        print(f"     • {len(import_jobs)} Import Jobs")
        print(f"     • {len(sla_violations)} SLA Violations")
        print(f"\n     TOTAL: ~{sum([len(quality_rules), len(check_runs), len(lineage_nodes), len(lineage_edges), len(schemas), len(sla_records), len(webhooks), len(deliveries), len(api_keys), len(integration_logs), len(tasks), len(notifications), len(comments), len(activity_logs), len(policies), len(validations), len(impact_runs), len(import_jobs), len(sla_violations)])} RECORDS!")
        print("\n  🎯 All Tool Pages Now Have Ample Data!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error seeding tools data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_tools()
