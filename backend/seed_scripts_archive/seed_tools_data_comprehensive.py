"""
COMPREHENSIVE Seed Data for ALL Tools & Features
Adds AMPLE sample data (20-50+ records per table) for all tool pages
"""
from app.database import SessionLocal, engine, Base
from app import models, models_extended, models_advanced, models_integrations, models_collaboration
from datetime import datetime, timedelta
import json
import random

def seed_comprehensive_tools_data():
    """Seed database with comprehensive tools sample data"""

    db = SessionLocal()

    try:
        print("\n" + "="*70)
        print("  🚀 COMPREHENSIVE TOOLS DATA SEEDING")
        print("="*70 + "\n")

        # ========================================
        # 1. DATA QUALITY RULES (20 rules)
        # ========================================
        print("Adding 20 Data Quality Rules...")
        rule_types = ["format", "uniqueness", "completeness", "range", "consistency", "timeliness"]
        severities = ["low", "medium", "high", "critical"]

        quality_rules = []
        rule_configs = [
            ("Employee ID Format", 1, 1, "employees", "employee_id", '{"pattern": "^EMP-[0-9]{6}$"}', "high"),
            ("Email Uniqueness", 1, 1, "employees", "email", '{"check": "unique"}', "critical"),
            ("Phone Format E.164", 1, 1, "employees", "phone", '{"pattern": "^\\+[1-9]\\d{1,14}$"}', "medium"),
            ("Department Code Valid", 1, 1, "employees", "department_code", '{"values": ["HR", "FIN", "IT", "OPS"]}', "high"),
            ("Hire Date Not Future", 1, 1, "employees", "hire_date", '{"max": "today"}', "critical"),

            ("Transaction Amount Range", 2, 2, "transactions", "amount", '{"min": 0.01, "max": 1000000.00}', "high"),
            ("Currency Code ISO", 2, 2, "transactions", "currency", '{"pattern": "^[A-Z]{3}$"}', "medium"),
            ("Transaction Date Recent", 2, 2, "transactions", "txn_date", '{"age_days": 90}', "low"),
            ("Account Number Length", 2, 2, "accounts", "account_number", '{"length": 16}', "critical"),
            ("Balance Non-Negative", 2, 2, "accounts", "balance", '{"min": 0}', "high"),

            ("Customer Email Format", 4, 4, "customers", "email", '{"pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}', "medium"),
            ("Customer Name Not Null", 4, 4, "customers", "name", '{"required": true}', "critical"),
            ("Customer Status Valid", 4, 4, "customers", "status", '{"values": ["active", "inactive", "suspended"]}', "high"),
            ("ZIP Code Format", 4, 4, "customers", "zip_code", '{"pattern": "^[0-9]{5}(-[0-9]{4})?$"}', "low"),
            ("Customer Age Range", 4, 4, "customers", "age", '{"min": 18, "max": 120}', "medium"),

            ("Asset Name Compliance", 1, 6, "assets", "asset_name", '{"pattern": "^(DEV|QA|UAT|PROD)-(HR|FIN|OPS|SALES|IT|DATA)-[A-Z0-9]+-v[0-9]+"}', "critical"),
            ("Asset Owner Not Null", 1, 6, "assets", "owner_id", '{"required": true}', "critical"),
            ("Asset Documentation URL", 1, 6, "assets", "documentation_url", '{"required": true, "pattern": "^https://"}', "medium"),
            ("Asset Domain Valid", 1, 6, "assets", "domain_id", '{"values": [1, 2, 3, 4, 5, 6]}', "high"),
            ("Asset Lifecycle Valid", 1, 6, "assets", "lifecycle_stage", '{"values": ["Draft", "Active", "Deprecated", "Retired"]}', "high"),
        ]

        for i, (name, asset_id, domain_id, table, column, logic, severity) in enumerate(rule_configs, 1):
            quality_rules.append(models_advanced.DataQualityRule(
                rule_name=name,
                rule_type=rule_types[i % len(rule_types)],
                description=f"Validate {column} in {table} table",
                target_table=table,
                target_column=column,
                validation_logic=logic,
                severity=severity,
                is_active=random.choice([True, True, True, False]),  # 75% active
                asset_id=asset_id,
                domain_id=domain_id,
                owner_id=random.randint(1, 3),
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
            total_records = random.randint(1000, 500000)
            failed = random.randint(0, int(total_records * 0.05))  # Up to 5% failure
            passed = total_records - failed
            pass_rate = (passed / total_records) * 100

            check_runs.append(models_advanced.QualityCheckRun(
                rule_id=rule_id,
                execution_time=datetime.now() - timedelta(hours=random.randint(1, 720)),  # Last 30 days
                records_checked=total_records,
                records_passed=passed,
                records_failed=failed,
                pass_rate=round(pass_rate, 2),
                status=random.choice(["completed", "completed", "completed", "failed"]),  # 75% complete
                error_details=f'{{"failed_count": {failed}}}' if failed > 0 else None,
                executed_by=random.randint(1, 3)
            ))

        db.add_all(check_runs)
        db.commit()
        print(f"✓ Created {len(check_runs)} quality check runs")

        # ========================================
        # 3. DATA LINEAGE NODES (40 nodes)
        # ========================================
        print("Adding 40 Data Lineage Nodes...")
        node_types = ["table", "view", "transformation", "pipeline", "api", "event"]
        lineage_nodes = []

        # HR nodes
        hr_nodes = [
            ("hr_employee_raw", "table", "Raw employee data from HRIS"),
            ("hr_employee_cleansed", "transformation", "Data cleansing transformation"),
            ("hr_employee_dw", "table", "Clean employee data warehouse table"),
            ("hr_payroll_source", "table", "Payroll system source data"),
            ("hr_payroll_transform", "transformation", "Payroll data transformation"),
            ("hr_payroll_dw", "table", "Payroll data warehouse"),
            ("hr_employee_api", "api", "Employee data REST API"),
            ("employee-updated-event", "event", "Employee record update event"),
        ]

        for i, (name, node_type, desc) in enumerate(hr_nodes, 1):
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=1,
                node_type=node_type,
                node_name=name,
                description=desc,
                location=f"s3://data-lake/hr/{name}/" if node_type == "table" else f"airflow://hr/{name}",
                schema_definition='{"columns": ["id", "name", "email"]}',
                row_count=random.randint(1000, 100000) if node_type == "table" else None,
                size_bytes=random.randint(1000000, 100000000) if node_type == "table" else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 48)),
                owner_id=random.randint(1, 3),
                domain_id=1,
                tags=f'["{node_type}", "hr"]'
            ))

        # Finance nodes
        fin_nodes = [
            ("finance_transactions_raw", "table", "Raw transaction data"),
            ("finance_ledger_source", "table", "General ledger source"),
            ("finance_etl_pipeline", "pipeline", "Finance ETL pipeline"),
            ("finance_dw_transactions", "table", "Transaction data warehouse"),
            ("finance_dw_accounts", "table", "Account balances data warehouse"),
            ("finance_reporting_view", "view", "Finance reporting view"),
            ("transaction-posted-event", "event", "Transaction posted event"),
            ("payment-processed-event", "event", "Payment processed event"),
        ]

        for name, node_type, desc in fin_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=2,
                node_type=node_type,
                node_name=name,
                description=desc,
                location=f"snowflake://prod/finance/{name}" if node_type in ["table", "view"] else f"airflow://finance/{name}",
                schema_definition='{"columns": ["txn_id", "amount", "currency"]}',
                row_count=random.randint(10000, 1000000) if node_type in ["table", "view"] else None,
                size_bytes=random.randint(10000000, 500000000) if node_type in ["table", "view"] else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 24)),
                owner_id=random.randint(1, 3),
                domain_id=2,
                tags=f'["{node_type}", "finance"]'
            ))

        # Ops nodes
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
                node_type=node_type,
                node_name=name,
                description=desc,
                location=f"postgres://ops/{name}",
                schema_definition='{"columns": ["order_id", "status"]}',
                row_count=random.randint(5000, 50000) if node_type == "table" else None,
                size_bytes=random.randint(5000000, 50000000) if node_type == "table" else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 72)),
                owner_id=random.randint(1, 3),
                domain_id=3,
                tags=f'["{node_type}", "operations"]'
            ))

        # Sales nodes
        sales_nodes = [
            ("sales_crm_contacts", "table", "CRM contacts data"),
            ("sales_opportunities", "table", "Sales opportunities"),
            ("sales_pipeline_view", "view", "Sales pipeline view"),
            ("deal-closed-event", "event", "Deal closed event"),
            ("lead-created-event", "event", "New lead created event"),
            ("sales_analytics_dw", "table", "Sales analytics warehouse"),
        ]

        for name, node_type, desc in sales_nodes:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=4,
                node_type=node_type,
                node_name=name,
                description=desc,
                location=f"salesforce://prod/{name}" if "crm" in name else f"redshift://sales/{name}",
                schema_definition='{"columns": ["customer_id", "amount"]}',
                row_count=random.randint(2000, 20000) if node_type in ["table", "view"] else None,
                size_bytes=random.randint(2000000, 20000000) if node_type in ["table", "view"] else None,
                last_updated=datetime.now() - timedelta(hours=random.randint(1, 168)),
                owner_id=random.randint(1, 3),
                domain_id=4,
                tags=f'["{node_type}", "sales"]'
            ))

        # Governance events
        gov_events = [
            ("asset-created-event", "event", "New asset created event"),
            ("compliance-violation-event", "event", "Compliance violation detected"),
            ("change-approved-event", "event", "Change request approved"),
            ("sla-breached-event", "event", "SLA target breached"),
            ("quality-check-failed-event", "event", "Data quality check failed"),
        ]

        for name, node_type, desc in gov_events:
            lineage_nodes.append(models_advanced.DataLineageNode(
                asset_id=1,
                node_type=node_type,
                node_name=name,
                description=desc,
                location=f"kafka://events/{name}",
                schema_definition='{"event_id": "string", "timestamp": "datetime"}',
                owner_id=1,
                domain_id=6,
                tags=f'["event", "governance", "kafka"]'
            ))

        db.add_all(lineage_nodes)
        db.commit()
        print(f"✓ Created {len(lineage_nodes)} lineage nodes")

        # ========================================
        # 4. DATA LINEAGE EDGES (30 edges)
        # ========================================
        print("Adding 30 Data Lineage Edges...")
        lineage_edges = []

        # Create edges connecting the nodes
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
                edge_type="dataflow",
                transformation_logic=f"Data flows from node {source_id} to {target_id}",
                data_volume_gb=round(random.uniform(0.1, 50.0), 2),
                latency_seconds=random.randint(10, 600),
                last_execution=datetime.now() - timedelta(hours=random.randint(1, 48))
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
            ("user-activity", 6, 6, "json"), ("audit-log", 6, 6, "avro"),
            ("notification-message", 6, 6, "json"), ("task-assignment", 6, 6, "json"),
            ("comment-thread", 6, 6, "json"), ("webhook-payload", 6, 6, "json"),
            ("api-request-log", 6, 6, "json"),
        ]

        for subject, asset_id, domain_id, format_type in subjects:
            version = random.randint(1, 5)
            schemas.append(models_advanced.SchemaRegistry(
                subject=subject,
                schema_format=format_type,
                version=version,
                schema_definition='{"type": "record", "name": "' + subject.replace("-", "_") + '", "fields": [{"name": "id", "type": "string"}]}',
                compatibility_mode=random.choice(["BACKWARD", "FORWARD", "FULL", "NONE"]),
                is_active=True,
                is_latest=True,
                asset_id=asset_id,
                domain_id=domain_id,
                created_by=1,
                description=f"Schema for {subject} data",
                changelog=f"v{version}: Latest version"
            ))

        db.add_all(schemas)
        db.commit()
        print(f"✓ Created {len(schemas)} schema registry entries")

        # ========================================
        # 6. SLA MONITORING (60 records)
        # ========================================
        print("Adding 60 SLA Monitoring records...")
        sla_records = []

        metric_configs = [
            ("Service Availability", "%", 99.95, 0.1),
            ("Query Response Time", "seconds", 3.0, 0.5),
            ("Data Processing Latency", "seconds", 300.0, 30.0),
            ("Support Response Time", "hours", 4.0, 1.0),
            ("API Response Time", "milliseconds", 200.0, 50.0),
            ("Data Freshness", "minutes", 15.0, 5.0),
            ("Backup Completion", "%", 100.0, 0.0),
            ("Error Rate", "%", 0.5, 0.2),
        ]

        # Generate records for last 30 days
        for days_ago in range(30):
            for metric_name, unit, target, variance in random.sample(metric_configs, k=2):  # 2 metrics per day
                actual = target + random.uniform(-variance, variance)
                breached = actual < target if "Rate" not in metric_name else actual > target

                sla_records.append(models_advanced.SLAMonitoring(
                    vendor_id=random.randint(1, 3),
                    asset_id=random.choice([1, 2, 3, 4, None]),
                    metric_name=metric_name,
                    target_value=target,
                    actual_value=round(actual, 2),
                    measurement_unit=unit,
                    measurement_timestamp=datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    status="breached" if breached else "met",
                    breached=breached
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
            ("Slack Governance Alerts", "https://hooks.slack.com/services/T00/B00/XXX", "#data-governance", '["compliance.violation", "change.approved", "asset.created"]'),
            ("Slack Quality Alerts", "https://hooks.slack.com/services/T00/B01/XXX", "#data-quality", '["quality.check.failed", "quality.rule.created"]'),
            ("Teams Change Notifications", "https://company.webhook.office.com/webhookb2/xxx1", "Change Management", '["change.requested", "change.approved", "change.rejected"]'),
            ("Teams SLA Alerts", "https://company.webhook.office.com/webhookb2/xxx2", "SLA Monitoring", '["sla.breached", "sla.warning"]'),
            ("ServiceNow Change Integration", "https://company.service-now.com/api/now/table/change_request", "Change tickets", '["change.requested", "change.approved"]'),
            ("ServiceNow Incident Integration", "https://company.service-now.com/api/now/table/incident", "Incident tickets", '["compliance.violation", "sla.breached"]'),
            ("PagerDuty Critical Alerts", "https://events.pagerduty.com/v2/enqueue", "On-call", '["sla.critical", "quality.critical", "compliance.critical"]'),
            ("Datadog Metrics", "https://api.datadoghq.com/api/v1/events", "Monitoring", '["asset.created", "asset.updated", "quality.check.completed"]'),
            ("Email Digest", "https://api.sendgrid.com/v3/mail/send", "Daily digest", '["asset.created", "change.approved"]'),
            ("Jira Issue Creation", "https://company.atlassian.net/rest/api/2/issue", "Issue tracking", '["compliance.violation", "quality.check.failed"]'),
            ("Confluence Doc Update", "https://company.atlassian.net/wiki/rest/api/content", "Documentation", '["asset.created", "schema.registered"]'),
            ("AWS EventBridge", "https://events.us-east-1.amazonaws.com/", "Event bus", '["asset.created", "asset.deleted", "change.approved"]'),
            ("Azure Event Grid", "https://eventgrid.azure.net/api/events", "Event hub", '["quality.check.completed", "sla.measured"]'),
            ("Custom Analytics Platform", "https://analytics.company.com/api/v1/events", "Analytics", '["asset.created", "quality.check.completed"]'),
            ("Audit Log Archive", "https://logs.company.com/api/v1/archive", "Long-term storage", '["audit.log", "change.approved"]'),
        ]

        for name, url, desc, events in webhook_configs:
            webhooks.append(models_integrations.Webhook(
                name=name,
                url=url,
                description=f"Webhook for {desc}",
                event_types=events,
                is_active=random.choice([True, True, True, False]),  # 75% active
                secret_key=f"webhook_secret_{random.randint(1000, 9999)}",
                headers='{"Content-Type": "application/json"}',
                retry_count=random.randint(3, 5),
                timeout_seconds=random.randint(30, 90),
                created_by=1
            ))

        db.add_all(webhooks)
        db.commit()
        print(f"✓ Created {len(webhooks)} webhooks")

        # ========================================
        # 8. WEBHOOK DELIVERIES (100 logs)
        # ========================================
        print("Adding 100 Webhook Delivery logs...")
        deliveries = []

        event_types = [
            "compliance.violation", "change.approved", "asset.created", "quality.check.failed",
            "sla.breached", "schema.registered", "change.requested", "asset.updated"
        ]

        for i in range(100):
            status = random.choice(["success", "success", "success", "failed"])  # 75% success
            webhook_id = random.randint(1, 15)

            deliveries.append(models_integrations.WebhookDelivery(
                webhook_id=webhook_id,
                event_type=random.choice(event_types),
                payload=f'{{"event_id": "{random.randint(1000, 9999)}", "timestamp": "{datetime.now().isoformat()}"}}',
                status=status,
                status_code=200 if status == "success" else random.choice([500, 503, 504]),
                response_body='{"ok": true}' if status == "success" else '{"error": "Internal error"}',
                delivered_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                retry_count=0 if status == "success" else random.randint(1, 3)
            ))

        db.add_all(deliveries)
        db.commit()
        print(f"✓ Created {len(deliveries)} webhook delivery logs")

        # ========================================
        # 9. API KEYS (20 keys)
        # ========================================
        print("Adding 20 API Keys...")
        api_keys = []

        key_configs = [
            ("ETL Pipeline Service Account", '["asset:read", "asset:create", "lineage:write"]', 90),
            ("Analytics Team Dashboard", '["asset:read", "compliance:read", "reports:read"]', 365),
            ("Monitoring Service", '["sla:read", "quality:read", "health:read"]', 30),
            ("CI/CD Automation", '["asset:create", "asset:update", "change:create"]', 180),
            ("Data Science Platform", '["asset:read", "lineage:read", "schema:read"]', 365),
            ("Business Intelligence Tool", '["asset:read", "reports:read"]', 365),
            ("External Partner API", '["asset:read"]', 90),
            ("Mobile App Backend", '["asset:read", "notifications:read"]', 180),
            ("Slack Integration Bot", '["asset:read", "change:read", "notifications:create"]', 365),
            ("Tableau Connector", '["asset:read", "schema:read"]', 365),
            ("Airflow DAG Runner", '["asset:read", "asset:update", "lineage:write"]', 180),
            ("Data Catalog Sync", '["asset:read", "asset:create", "schema:read", "schema:write"]', 365),
            ("Compliance Auditor", '["asset:read", "compliance:read", "audit:read"]', 180),
            ("Backup Service", '["asset:read"]', 365),
            ("Testing Framework", '["asset:read", "asset:create", "asset:delete"]', 90),
            ("Documentation Generator", '["asset:read", "schema:read"]', 365),
            ("Cost Management Tool", '["asset:read", "vendor:read", "budget:read"]', 180),
            ("Security Scanner", '["asset:read", "compliance:read"]', 180),
            ("Performance Monitor", '["asset:read", "sla:read", "quality:read"]', 90),
            ("Developer Sandbox", '["asset:read", "asset:create"]', 30),
        ]

        for name, scopes, expiry_days in key_configs:
            is_active = random.choice([True, True, True, False])  # 75% active
            api_keys.append(models_integrations.APIKey(
                key_name=name,
                key_hash=f"$2b$12${''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=40))}",
                description=f"API key for {name.lower()}",
                scopes=scopes,
                is_active=is_active,
                expires_at=datetime.now() + timedelta(days=expiry_days),
                created_by=random.randint(1, 3),
                last_used=datetime.now() - timedelta(hours=random.randint(1, 720)) if is_active else None
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
        event_types_extended = event_types + ["sync.completed", "export.completed", "import.started"]

        for i in range(150):
            integration_type = random.choice(integration_types)
            status = random.choice(["success", "success", "success", "error"])  # 75% success

            integration_logs.append(models_integrations.IntegrationLog(
                integration_type=integration_type,
                integration_name=f"{integration_type.title()} Integration {random.randint(1, 20)}",
                event_type=random.choice(event_types_extended),
                status=status,
                request_payload=f'{{"request_id": "{random.randint(10000, 99999)}"}}',
                response_payload='{"success": true}' if status == "success" else '{"error": "Failed"}',
                status_code=200 if status == "success" else random.choice([400, 500, 503]),
                execution_time_ms=random.randint(50, 5000),
                error_message=None if status == "success" else "Integration error occurred",
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720))
            ))

        db.add_all(integration_logs)
        db.commit()
        print(f"✓ Created {len(integration_logs)} integration logs")

        # ========================================
        # 11. TASKS (40 tasks)
        # ========================================
        print("Adding 40 Tasks...")
        tasks = []

        task_types = ["review", "approval", "documentation", "investigation", "remediation"]
        priorities = ["low", "medium", "high", "critical"]
        statuses = ["pending", "in_progress", "completed", "cancelled"]

        task_titles = [
            "Review asset naming compliance",
            "Approve change request for production deployment",
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
            assigned_to = random.randint(1, 5)
            created_by = random.randint(1, 3)
            due_date = datetime.now() + timedelta(days=random.randint(1, 30))
            status = random.choice(statuses)

            tasks.append(models_collaboration.Task(
                title=random.choice(task_titles),
                description=f"Task description {i+1}: Please complete this assigned task.",
                task_type=random.choice(task_types),
                priority=random.choice(priorities),
                status=status,
                assigned_to=assigned_to,
                created_by=created_by,
                due_date=due_date,
                completed_at=datetime.now() - timedelta(days=random.randint(1, 10)) if status == "completed" else None,
                asset_id=random.choice([None, 1, 2, 3, 4]),
                change_request_id=random.choice([None, 1])
            ))

        db.add_all(tasks)
        db.commit()
        print(f"✓ Created {len(tasks)} tasks")

        # ========================================
        # 12. NOTIFICATIONS (60 notifications)
        # ========================================
        print("Adding 60 Notifications...")
        notifications = []

        notification_types = ["info", "warning", "error", "success"]

        for i in range(60):
            user_id = random.randint(1, 5)
            notif_type = random.choice(notification_types)
            is_read = random.choice([True, False])

            titles = {
                "info": ["New asset created", "Schema updated", "Task assigned"],
                "warning": ["SLA approaching threshold", "Upcoming compliance deadline", "Pending approval"],
                "error": ["Data quality check failed", "SLA breached", "Compliance violation detected"],
                "success": ["Change approved", "Quality check passed", "Task completed"]
            }

            notifications.append(models_collaboration.Notification(
                user_id=user_id,
                type=notif_type,
                title=random.choice(titles[notif_type]),
                message=f"Notification message {i+1} with detailed information about the event.",
                link=f"/assets/{random.randint(1, 5)}" if random.choice([True, False]) else None,
                is_read=is_read,
                read_at=datetime.now() - timedelta(hours=random.randint(1, 48)) if is_read else None,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720))
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
            "This looks good to me, approved!",
            "Can we schedule this for next week?",
            "I have some concerns about the impact on downstream systems.",
            "Please update the documentation before proceeding.",
            "What is the rollback plan?",
            "Has this been tested in QA environment?",
            "Approved with conditions - see inline comments.",
            "Please coordinate with the infrastructure team.",
            "This needs security review first.",
            "Great work! Ready to deploy.",
        ]

        for i in range(80):
            entity_type = random.choice(["asset", "change_request", "task"])
            entity_id = random.randint(1, 5)
            user_id = random.randint(1, 5)
            parent_comment_id = random.choice([None, None, random.randint(1, max(1, i-1))]) # 33% are replies

            comments.append(models_collaboration.Comment(
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                comment_text=random.choice(comment_texts),
                parent_comment_id=parent_comment_id,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720))
            ))

        db.add_all(comments)
        db.commit()
        print(f"✓ Created {len(comments)} comments")

        # ========================================
        # 14. ACTIVITY LOGS (200 activities)
        # ========================================
        print("Adding 200 Activity Logs...")
        activity_logs = []

        activity_types = [
            "asset_created", "asset_updated", "asset_deleted",
            "change_requested", "change_approved", "change_rejected",
            "compliance_violation_detected", "compliance_violation_resolved",
            "quality_check_passed", "quality_check_failed",
            "sla_met", "sla_breached",
            "schema_registered", "schema_updated",
            "user_login", "user_logout",
            "task_created", "task_completed",
            "comment_added", "notification_sent",
        ]

        for i in range(200):
            user_id = random.randint(1, 5)
            activity_type = random.choice(activity_types)
            entity_type = activity_type.split("_")[0] if "_" in activity_type else "system"

            activity_logs.append(models_collaboration.ActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                entity_type=entity_type,
                entity_id=random.randint(1, 20),
                description=f"User performed {activity_type.replace('_', ' ')}",
                metadata=f'{{"ip": "192.168.1.{random.randint(1, 255)}", "user_agent": "Mozilla/5.0"}}',
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
            ("Naming Convention Enforcement", "naming", "All assets must follow ENV-DOMAIN-SYSTEM-VERSION naming convention"),
            ("Documentation Requirement", "documentation", "All production assets must have documentation URL"),
            ("Change Approval Workflow", "change_management", "All production changes require data steward approval"),
            ("Data Quality Thresholds", "quality", "Quality check pass rate must be >= 95%"),
            ("SLA Monitoring", "sla", "All critical services must have SLA monitoring enabled"),
            ("Schema Versioning", "schema", "All schema changes must be versioned"),
            ("PII Data Handling", "security", "All PII data must be encrypted and access-controlled"),
            ("Data Retention", "compliance", "Data retention must comply with regulatory requirements"),
            ("Access Control", "security", "Role-based access control must be enforced"),
            ("Audit Logging", "compliance", "All data access must be logged for audit"),
            ("Disaster Recovery", "operations", "All critical assets must have DR plan"),
            ("Performance Standards", "performance", "API response time must be < 200ms"),
            ("Data Lineage Tracking", "lineage", "All data transformations must be documented"),
            ("Cost Optimization", "operations", "Unused assets must be archived or deleted"),
            ("Vendor Management", "vendor", "All vendors must have signed DPA"),
        ]

        for name, policy_type, desc in policy_configs:
            policies.append(models_advanced.GovernancePolicy(
                policy_name=name,
                policy_type=policy_type,
                description=desc,
                enforcement_level=random.choice(["advisory", "warning", "blocking"]),
                is_active=True,
                owner_id=random.randint(1, 2),
                created_by=1,
                policy_rules=f'{{"rule": "Policy rule definition for {name}"}}'
            ))

        db.add_all(policies)
        db.commit()
        print(f"✓ Created {len(policies)} governance policies")

        # ========================================
        # 16. POLICY VALIDATIONS (50 validations)
        # ========================================
        print("Adding 50 Policy Validation records...")
        validations = []

        for i in range(50):
            policy_id = random.randint(1, 15)
            passed = random.choice([True, True, True, False])  # 75% pass

            validations.append(models_advanced.PolicyValidation(
                policy_id=policy_id,
                asset_id=random.choice([1, 2, 3, 4, 5]),
                validation_result=passed,
                validation_details=f'{{"passed": {str(passed).lower()}}}',
                validated_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                validated_by=random.randint(1, 3)
            ))

        db.add_all(validations)
        db.commit()
        print(f"✓ Created {len(validations)} policy validations")

        # ========================================
        # 17. IMPACT ANALYSIS RUNS (30 runs)
        # ========================================
        print("Adding 30 Impact Analysis runs...")
        impact_runs = []

        for i in range(30):
            asset_id = random.randint(1, 5)
            impact_count = random.randint(5, 50)

            impact_runs.append(models_advanced.ImpactAnalysisRun(
                asset_id=asset_id,
                analysis_type=random.choice(["downstream", "upstream", "full"]),
                impacted_assets_count=impact_count,
                impact_details=f'{{"impacted_count": {impact_count}, "severity": "{"high" if impact_count > 30 else "medium"}"}}',
                analyzed_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                analyzed_by=random.randint(1, 3)
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
        import_types = ["asset_bulk_import", "schema_import", "lineage_import", "metadata_sync"]

        for i in range(25):
            status = random.choice(job_statuses)
            total_records = random.randint(10, 500)
            imported = random.randint(0, total_records) if status in ["completed", "failed"] else 0
            failed = total_records - imported if status == "failed" else 0

            import_jobs.append(models_integrations.ImportJob(
                job_name=f"Import Job {i+1}",
                job_type=random.choice(import_types),
                status=status,
                file_path=f"s3://imports/job_{i+1}.csv",
                total_records=total_records,
                imported_records=imported,
                failed_records=failed,
                error_log=f'{{"errors": [{{"row": {random.randint(1, 100)}, "error": "Invalid format"}}]}}' if failed > 0 else None,
                created_by=random.randint(1, 3),
                started_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if status != "pending" else None,
                completed_at=datetime.now() - timedelta(hours=random.randint(1, 720)) if status == "completed" else None
            ))

        db.add_all(import_jobs)
        db.commit()
        print(f"✓ Created {len(import_jobs)} import jobs")

        print("\n" + "="*70)
        print("  ✅ COMPREHENSIVE TOOLS DATA SEEDING COMPLETE!")
        print("="*70)
        print("\n  📊 Summary of Data Created:")
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
        print(f"\n     TOTAL: ~{sum([len(quality_rules), len(check_runs), len(lineage_nodes), len(lineage_edges), len(schemas), len(sla_records), len(webhooks), len(deliveries), len(api_keys), len(integration_logs), len(tasks), len(notifications), len(comments), len(activity_logs), len(policies), len(validations), len(impact_runs), len(import_jobs)])} RECORDS!")
        print("\n  🎯 All Tool Pages Now Have Ample Data!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error seeding comprehensive tools data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_comprehensive_tools_data()
