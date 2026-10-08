"""
Seed data for Tools section
Adds sample data for Data Quality, Data Lineage, Schema Registry, SLA Monitoring, Events, Webhooks, etc.
"""
from app.database import SessionLocal, engine, Base
from app import models_advanced, models_integrations
from datetime import datetime, timedelta
import json

def seed_tools_data():
    """Seed database with tools-specific sample data"""

    db = SessionLocal()

    try:
        print("\n" + "="*60)
        print("  SEEDING TOOLS DATA")
        print("="*60 + "\n")

        # ========================================
        # 1. DATA QUALITY RULES
        # ========================================
        print("Adding Data Quality Rules...")
        quality_rules = [
            models_advanced.DataQualityRule(
                rule_name="Employee ID Format Check",
                rule_type="format",
                description="Validate employee ID follows pattern: EMP-XXXXXX",
                target_table="employees",
                target_column="employee_id",
                validation_logic='{"pattern": "^EMP-[0-9]{6}$"}',
                severity="high",
                is_active=True,
                asset_id=1,  # HR Data Warehouse
                domain_id=1,  # HR
                owner_id=1,
                created_by=1
            ),
            models_advanced.DataQualityRule(
                rule_name="Email Uniqueness Check",
                rule_type="uniqueness",
                description="Ensure email addresses are unique across all employees",
                target_table="employees",
                target_column="email",
                validation_logic='{"check": "unique"}',
                severity="critical",
                is_active=True,
                asset_id=1,
                domain_id=1,
                owner_id=1,
                created_by=1
            ),
            models_advanced.DataQualityRule(
                rule_name="Transaction Amount Range",
                rule_type="range",
                description="Transaction amounts must be between $0.01 and $1,000,000",
                target_table="transactions",
                target_column="amount",
                validation_logic='{"min": 0.01, "max": 1000000.00}',
                severity="high",
                is_active=True,
                asset_id=2,  # Finance ETL
                domain_id=2,  # FIN
                owner_id=1,
                created_by=1
            ),
            models_advanced.DataQualityRule(
                rule_name="Customer Phone Format",
                rule_type="format",
                description="Phone numbers must follow E.164 format",
                target_table="customers",
                target_column="phone",
                validation_logic='{"pattern": "^\\+[1-9]\\d{1,14}$"}',
                severity="medium",
                is_active=True,
                asset_id=4,  # Sales CRM
                domain_id=4,  # SALES
                owner_id=1,
                created_by=1
            ),
            models_advanced.DataQualityRule(
                rule_name="Null Check - Required Fields",
                rule_type="completeness",
                description="Critical fields must not be NULL",
                target_table="assets",
                target_column="asset_name,owner_id,domain_id",
                validation_logic='{"required": true}',
                severity="critical",
                is_active=True,
                asset_id=1,
                domain_id=6,  # DATA
                owner_id=1,
                created_by=1
            ),
        ]
        db.add_all(quality_rules)
        db.commit()
        print(f"✓ Created {len(quality_rules)} data quality rules")

        # ========================================
        # 2. QUALITY CHECK RUNS
        # ========================================
        print("Adding Quality Check Runs...")
        check_runs = [
            models_advanced.QualityCheckRun(
                rule_id=1,
                execution_time=datetime.now() - timedelta(hours=2),
                records_checked=15234,
                records_passed=15180,
                records_failed=54,
                pass_rate=99.65,
                status="completed",
                error_details='{"sample_failures": ["EMP-12A456", "EMP-789"]}',
                executed_by=1
            ),
            models_advanced.QualityCheckRun(
                rule_id=2,
                execution_time=datetime.now() - timedelta(hours=1),
                records_checked=15234,
                records_passed=15230,
                records_failed=4,
                pass_rate=99.97,
                status="completed",
                error_details='{"duplicate_emails": 4}',
                executed_by=1
            ),
            models_advanced.QualityCheckRun(
                rule_id=3,
                execution_time=datetime.now() - timedelta(minutes=30),
                records_checked=456789,
                records_passed=456234,
                records_failed=555,
                pass_rate=99.88,
                status="completed",
                error_details='{"out_of_range": 555}',
                executed_by=1
            ),
        ]
        db.add_all(check_runs)
        db.commit()
        print(f"✓ Created {len(check_runs)} quality check runs")

        # ========================================
        # 3. DATA LINEAGE NODES
        # ========================================
        print("Adding Data Lineage Nodes...")
        lineage_nodes = [
            # Source nodes
            models_advanced.DataLineageNode(
                asset_id=1,
                node_type="table",
                node_name="hr_employee_source",
                description="Source table for employee data from HR system",
                location="s3://data-lake/raw/hr/employees/",
                schema_definition='{"columns": ["emp_id", "name", "email", "dept"]}',
                row_count=15234,
                size_bytes=5242880,
                last_updated=datetime.now() - timedelta(hours=6),
                owner_id=1,
                domain_id=1,
                tags='["source", "hr", "pii"]'
            ),
            # Transform nodes
            models_advanced.DataLineageNode(
                asset_id=1,
                node_type="transformation",
                node_name="hr_employee_cleanse",
                description="Data cleansing and validation transformation",
                location="airflow://dags/hr_etl/cleanse_step",
                schema_definition='{"transformations": ["dedupe", "format_phone", "validate_email"]}',
                last_updated=datetime.now() - timedelta(hours=5),
                owner_id=1,
                domain_id=1,
                tags='["transformation", "etl"]'
            ),
            # Target nodes
            models_advanced.DataLineageNode(
                asset_id=1,
                node_type="table",
                node_name="hr_employee_dw",
                description="Data warehouse table for clean employee data",
                location="snowflake://prod/hr_dw/employees",
                schema_definition='{"columns": ["employee_id", "full_name", "email", "department", "hire_date"]}',
                row_count=15180,
                size_bytes=7340032,
                last_updated=datetime.now() - timedelta(hours=1),
                owner_id=1,
                domain_id=1,
                tags='["target", "warehouse", "production"]'
            ),
            # Finance nodes
            models_advanced.DataLineageNode(
                asset_id=2,
                node_type="table",
                node_name="finance_transactions",
                description="Daily financial transactions",
                location="s3://data-lake/raw/finance/transactions/",
                schema_definition='{"columns": ["txn_id", "amount", "currency", "timestamp"]}',
                row_count=456789,
                size_bytes=52428800,
                last_updated=datetime.now() - timedelta(hours=2),
                owner_id=1,
                domain_id=2,
                tags='["source", "finance"]'
            ),
            # Event nodes (for Event Catalog)
            models_advanced.DataLineageNode(
                asset_id=1,
                node_type="event",
                node_name="asset-created-event",
                description="Event published when a new asset is created",
                location="kafka://events/asset-created",
                schema_definition='{"schema": {"asset_id": "string", "asset_name": "string", "timestamp": "datetime"}}',
                owner_id=1,
                domain_id=6,
                tags='["event", "kafka", "governance"]'
            ),
            models_advanced.DataLineageNode(
                asset_id=1,
                node_type="event",
                node_name="compliance-violation-event",
                description="Event published when compliance violation is detected",
                location="kafka://events/compliance-violation",
                schema_definition='{"schema": {"asset_id": "string", "violation_type": "string", "severity": "string"}}',
                owner_id=1,
                domain_id=6,
                tags='["event", "kafka", "compliance"]'
            ),
        ]
        db.add_all(lineage_nodes)
        db.commit()
        print(f"✓ Created {len(lineage_nodes)} lineage nodes (including events)")

        # ========================================
        # 4. DATA LINEAGE EDGES
        # ========================================
        print("Adding Data Lineage Edges...")
        lineage_edges = [
            # Source -> Transform
            models_advanced.DataLineageEdge(
                source_node_id=1,  # hr_employee_source
                target_node_id=2,  # hr_employee_cleanse
                edge_type="dataflow",
                transformation_logic="Extract employee data from S3 and apply cleansing rules",
                data_volume_gb=5.0,
                latency_seconds=120,
                last_execution=datetime.now() - timedelta(hours=5)
            ),
            # Transform -> Target
            models_advanced.DataLineageEdge(
                source_node_id=2,  # hr_employee_cleanse
                target_node_id=3,  # hr_employee_dw
                edge_type="dataflow",
                transformation_logic="Load cleansed data into Snowflake warehouse",
                data_volume_gb=7.0,
                latency_seconds=180,
                last_execution=datetime.now() - timedelta(hours=1)
            ),
        ]
        db.add_all(lineage_edges)
        db.commit()
        print(f"✓ Created {len(lineage_edges)} lineage edges")

        # ========================================
        # 5. SCHEMA REGISTRY
        # ========================================
        print("Adding Schema Registry entries...")
        schemas = [
            models_advanced.SchemaRegistry(
                subject="hr-employee",
                schema_format="avro",
                version=3,
                schema_definition='{"type": "record", "name": "Employee", "fields": [{"name": "employee_id", "type": "string"}, {"name": "email", "type": "string"}, {"name": "department", "type": "string"}]}',
                compatibility_mode="BACKWARD",
                is_active=True,
                is_latest=True,
                asset_id=1,
                domain_id=1,
                created_by=1,
                description="Employee record schema with backward compatibility",
                changelog="v3: Added department field"
            ),
            models_advanced.SchemaRegistry(
                subject="finance-transaction",
                schema_format="json",
                version=2,
                schema_definition='{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {"transaction_id": {"type": "string"}, "amount": {"type": "number"}, "currency": {"type": "string"}, "timestamp": {"type": "string", "format": "date-time"}}}',
                compatibility_mode="FULL",
                is_active=True,
                is_latest=True,
                asset_id=2,
                domain_id=2,
                created_by=1,
                description="Financial transaction JSON schema",
                changelog="v2: Added currency field"
            ),
            models_advanced.SchemaRegistry(
                subject="asset-created-event",
                schema_format="avro",
                version=1,
                schema_definition='{"type": "record", "name": "AssetCreated", "fields": [{"name": "asset_id", "type": "int"}, {"name": "asset_name", "type": "string"}, {"name": "timestamp", "type": "long"}]}',
                compatibility_mode="FORWARD",
                is_active=True,
                is_latest=True,
                asset_id=1,
                domain_id=6,
                created_by=1,
                description="Schema for asset creation events",
                examples='[{"asset_id": 123, "asset_name": "PROD-HR-DW-v1", "timestamp": 1640000000000}]'
            ),
        ]
        db.add_all(schemas)
        db.commit()
        print(f"✓ Created {len(schemas)} schema registry entries")

        # ========================================
        # 6. SLA MONITORING
        # ========================================
        print("Adding SLA Monitoring records...")
        sla_records = [
            models_advanced.SLAMonitoring(
                vendor_id=1,  # AWS
                asset_id=1,
                metric_name="Service Availability",
                target_value=99.95,
                actual_value=99.97,
                measurement_unit="%",
                measurement_timestamp=datetime.now() - timedelta(hours=1),
                status="met",
                breached=False
            ),
            models_advanced.SLAMonitoring(
                vendor_id=2,  # Snowflake
                asset_id=1,
                metric_name="Query Response Time",
                target_value=3.0,
                actual_value=2.1,
                measurement_unit="seconds",
                measurement_timestamp=datetime.now() - timedelta(minutes=30),
                status="met",
                breached=False
            ),
            models_advanced.SLAMonitoring(
                vendor_id=1,
                asset_id=2,
                metric_name="Data Processing Latency",
                target_value=300.0,
                actual_value=285.0,
                measurement_unit="seconds",
                measurement_timestamp=datetime.now() - timedelta(minutes=15),
                status="met",
                breached=False
            ),
            models_advanced.SLAMonitoring(
                vendor_id=3,  # Tableau
                metric_name="Support Response Time",
                target_value=4.0,
                actual_value=2.5,
                measurement_unit="hours",
                measurement_timestamp=datetime.now() - timedelta(hours=2),
                status="met",
                breached=False
            ),
        ]
        db.add_all(sla_records)
        db.commit()
        print(f"✓ Created {len(sla_records)} SLA monitoring records")

        # ========================================
        # 7. WEBHOOKS
        # ========================================
        print("Adding Webhooks...")
        webhooks = [
            models_integrations.Webhook(
                name="Slack Governance Alerts",
                url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
                description="Send governance alerts to #data-governance Slack channel",
                event_types='["compliance.violation", "change.approved", "asset.created"]',
                is_active=True,
                secret_key="slack_webhook_secret_12345",
                headers='{"Content-Type": "application/json"}',
                retry_count=3,
                timeout_seconds=30,
                created_by=1
            ),
            models_integrations.Webhook(
                name="ServiceNow Change Integration",
                url="https://company.service-now.com/api/now/table/change_request",
                description="Create ServiceNow change tickets for asset deployments",
                event_types='["change.requested", "change.approved"]',
                is_active=True,
                secret_key="servicenow_api_key",
                headers='{"Content-Type": "application/json", "Authorization": "Bearer xxx"}',
                retry_count=5,
                timeout_seconds=60,
                created_by=1
            ),
            models_integrations.Webhook(
                name="Teams Data Quality Notifications",
                url="https://company.webhook.office.com/webhookb2/xxx",
                description="Send data quality alerts to Microsoft Teams",
                event_types='["quality.check.failed", "quality.rule.created"]',
                is_active=True,
                secret_key="teams_webhook_secret",
                headers='{"Content-Type": "application/json"}',
                retry_count=3,
                timeout_seconds=30,
                created_by=1
            ),
        ]
        db.add_all(webhooks)
        db.commit()
        print(f"✓ Created {len(webhooks)} webhooks")

        # ========================================
        # 8. WEBHOOK DELIVERIES (Sample logs)
        # ========================================
        print("Adding Webhook Delivery logs...")
        deliveries = [
            models_integrations.WebhookDelivery(
                webhook_id=1,
                event_type="compliance.violation",
                payload='{"asset_id": 5, "violation_type": "Naming", "severity": "High"}',
                status="success",
                status_code=200,
                response_body='{"ok": true}',
                delivered_at=datetime.now() - timedelta(hours=3),
                retry_count=0
            ),
            models_integrations.WebhookDelivery(
                webhook_id=2,
                event_type="change.approved",
                payload='{"change_id": 1, "asset_id": 1, "approver": "jsmith"}',
                status="success",
                status_code=201,
                response_body='{"result": {"sys_id": "abc123"}}',
                delivered_at=datetime.now() - timedelta(hours=1),
                retry_count=0
            ),
            models_integrations.WebhookDelivery(
                webhook_id=3,
                event_type="quality.check.failed",
                payload='{"rule_id": 1, "failed_records": 54}',
                status="failed",
                status_code=500,
                response_body='{"error": "Internal Server Error"}',
                delivered_at=datetime.now() - timedelta(minutes=30),
                retry_count=3
            ),
        ]
        db.add_all(deliveries)
        db.commit()
        print(f"✓ Created {len(deliveries)} webhook delivery logs")

        # ========================================
        # 9. API KEYS
        # ========================================
        print("Adding API Keys...")
        api_keys = [
            models_integrations.APIKey(
                key_name="ETL Pipeline Service Account",
                key_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/0hY9t5w5K3e",  # Hashed "etl_key_12345"
                description="API key for automated ETL pipeline operations",
                scopes='["asset:read", "asset:create", "lineage:write"]',
                is_active=True,
                expires_at=datetime.now() + timedelta(days=90),
                created_by=1,
                last_used=datetime.now() - timedelta(hours=2)
            ),
            models_integrations.APIKey(
                key_name="Analytics Team Read Access",
                key_hash="$2b$12$abc123xyz789hashedkeyvalue",
                description="Read-only access for analytics team dashboards",
                scopes='["asset:read", "compliance:read", "reports:read"]',
                is_active=True,
                expires_at=datetime.now() + timedelta(days=365),
                created_by=1,
                last_used=datetime.now() - timedelta(days=1)
            ),
            models_integrations.APIKey(
                key_name="Monitoring Service",
                key_hash="$2b$12$monitoring_key_hash_value",
                description="API key for external monitoring and alerting service",
                scopes='["sla:read", "quality:read", "health:read"]',
                is_active=True,
                expires_at=datetime.now() + timedelta(days=30),
                created_by=1,
                last_used=datetime.now() - timedelta(minutes=15)
            ),
        ]
        db.add_all(api_keys)
        db.commit()
        print(f"✓ Created {len(api_keys)} API keys")

        # ========================================
        # 10. INTEGRATION LOGS
        # ========================================
        print("Adding Integration Logs...")
        integration_logs = [
            models_integrations.IntegrationLog(
                integration_type="webhook",
                integration_name="Slack Governance Alerts",
                event_type="compliance.violation",
                status="success",
                request_payload='{"asset_id": 5, "type": "naming"}',
                response_payload='{"ok": true, "message": "posted"}',
                status_code=200,
                execution_time_ms=234,
                error_message=None,
                created_at=datetime.now() - timedelta(hours=3)
            ),
            models_integrations.IntegrationLog(
                integration_type="api",
                integration_name="ETL Pipeline Service Account",
                event_type="asset.create",
                status="success",
                request_payload='{"asset_name": "PROD-DATA-LAKE-v2"}',
                response_payload='{"asset_id": 10}',
                status_code=201,
                execution_time_ms=567,
                error_message=None,
                created_at=datetime.now() - timedelta(hours=2)
            ),
            models_integrations.IntegrationLog(
                integration_type="webhook",
                integration_name="Teams Data Quality Notifications",
                event_type="quality.check.failed",
                status="error",
                request_payload='{"rule_id": 1}',
                response_payload='{"error": "timeout"}',
                status_code=500,
                execution_time_ms=30000,
                error_message="Request timeout after 30 seconds",
                created_at=datetime.now() - timedelta(minutes=30)
            ),
        ]
        db.add_all(integration_logs)
        db.commit()
        print(f"✓ Created {len(integration_logs)} integration logs")

        print("\n" + "="*60)
        print("  ✅ TOOLS DATA SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\n  📊 Tools Data Created:")
        print(f"     • {len(quality_rules)} Data Quality Rules")
        print(f"     • {len(check_runs)} Quality Check Runs")
        print(f"     • {len(lineage_nodes)} Data Lineage Nodes (incl. Events)")
        print(f"     • {len(lineage_edges)} Data Lineage Edges")
        print(f"     • {len(schemas)} Schema Registry Entries")
        print(f"     • {len(sla_records)} SLA Monitoring Records")
        print(f"     • {len(webhooks)} Webhooks")
        print(f"     • {len(deliveries)} Webhook Delivery Logs")
        print(f"     • {len(api_keys)} API Keys")
        print(f"     • {len(integration_logs)} Integration Logs")
        print("\n  🔧 Tools Pages Now Have Data:")
        print("     • Data Quality Dashboard")
        print("     • Data Lineage Visualization")
        print("     • Schema Registry")
        print("     • Event Catalog")
        print("     • SLA Monitoring")
        print("     • Webhook Management")
        print("     • API Key Management")
        print("     • Integration Logs")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error seeding tools data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_tools_data()
