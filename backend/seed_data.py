"""
Database seeding script
Initializes database with sample data for demonstration
"""
from app.database import SessionLocal, engine, Base
from app import models, models_extended
from app.auth import get_password_hash
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_database():
    """Seed database with sample data"""

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(models.Role).count() > 0:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # 1. Create Roles
        roles = [
            models.Role(role_name="Admin", description="Full system access", permissions='["*"]'),
            models.Role(role_name="DataSteward", description="Governance and approval authority",
                       permissions='["asset:*", "change:approve", "compliance:view"]'),
            models.Role(role_name="AssetOwner", description="Manage owned assets",
                       permissions='["asset:create", "asset:update", "asset:view"]'),
            models.Role(role_name="Viewer", description="Read-only access",
                       permissions='["asset:view", "compliance:view"]'),
        ]
        db.add_all(roles)
        db.commit()
        print("✓ Roles created")

        # 2. Create Users (password: demo123 - using bcrypt hashing)
        hashed_password = get_password_hash("demo123")
        users = [
            models.User(username="admin", email="admin@company.com", password_hash=hashed_password,
                       first_name="System", last_name="Admin", role_id=1, is_active=True),
            models.User(username="jsmith", email="jsmith@company.com", password_hash=hashed_password,
                       first_name="John", last_name="Smith", role_id=2, is_active=True),
            models.User(username="mjohnson", email="mjohnson@company.com", password_hash=hashed_password,
                       first_name="Mary", last_name="Johnson", role_id=3, is_active=True),
            models.User(username="rdavis", email="rdavis@company.com", password_hash=hashed_password,
                       first_name="Robert", last_name="Davis", role_id=4, is_active=True),
            models.User(username="cthomas", email="cthomas@company.com", password_hash=hashed_password,
                       first_name="Carol", last_name="Thomas", role_id=3, is_active=True),
        ]
        db.add_all(users)
        db.commit()
        print("✓ Users created")

        # 3. Create Domains
        domains = [
            models.Domain(domain_code="HR", domain_name="Human Resources",
                         description="Employee and workforce management data", data_steward_id=2, is_active=True),
            models.Domain(domain_code="FIN", domain_name="Finance",
                         description="Financial transactions and accounting data", data_steward_id=2, is_active=True),
            models.Domain(domain_code="OPS", domain_name="Operations",
                         description="Operational and logistics data", data_steward_id=2, is_active=True),
            models.Domain(domain_code="SALES", domain_name="Sales",
                         description="Sales and customer relationship data", data_steward_id=2, is_active=True),
            models.Domain(domain_code="IT", domain_name="Information Technology",
                         description="IT infrastructure and systems data", data_steward_id=2, is_active=True),
            models.Domain(domain_code="DATA", domain_name="Data Platform",
                         description="Enterprise data platform assets", data_steward_id=2, is_active=True),
        ]
        db.add_all(domains)
        db.commit()
        print("✓ Domains created")

        # 4. Create Sample Assets
        assets = [
            models.Asset(
                asset_name="PROD-HR-DW-v1", domain_id=1, environment="PROD", owner_id=3, version="v1.0",
                lifecycle_stage="Active", documentation_url="https://docs.company.com/hr-dw",
                description="HR Data Warehouse - central repository for employee data",
                business_justification="Centralize HR data for reporting and analytics",
                naming_compliant=True, created_by=1
            ),
            models.Asset(
                asset_name="PROD-FIN-ETL-v2", domain_id=2, environment="PROD", owner_id=3, version="v2.1",
                lifecycle_stage="Active", documentation_url="https://docs.company.com/fin-etl",
                description="Finance ETL Pipeline - daily transaction processing",
                business_justification="Automate financial data ingestion", naming_compliant=True, created_by=1
            ),
            models.Asset(
                asset_name="QA-OPS-API-v1", domain_id=3, environment="QA", owner_id=3, version="v1.3",
                lifecycle_stage="Active", documentation_url="https://docs.company.com/ops-api",
                description="Operations API - logistics data access layer",
                business_justification="Provide unified API for operations data", naming_compliant=True, created_by=1
            ),
            models.Asset(
                asset_name="DEV-SALES-CRM-v3", domain_id=4, environment="DEV", owner_id=3, version="v3.0",
                lifecycle_stage="Draft", documentation_url="",
                description="Sales CRM Integration - Salesforce connector",
                business_justification="Integrate Salesforce data", naming_compliant=True, created_by=1
            ),
            models.Asset(
                asset_name="production-finance-system", domain_id=2, environment="PROD", owner_id=3, version="v1",
                lifecycle_stage="Active", documentation_url="",
                description="Non-compliant naming example",
                business_justification="Legacy system", naming_compliant=False, created_by=1
            ),
        ]
        db.add_all(assets)
        db.commit()
        print("✓ Assets created")

        # 5. Create Compliance Violation for non-compliant asset
        violation = models.ComplianceViolation(
            asset_id=5, violation_type="Naming", severity="High",
            description="Asset name does not comply with standard format ENV-DOMAIN-SYSTEM-VERSION"
        )
        db.add(violation)
        db.commit()
        print("✓ Compliance violations created")

        # 6. Create Sample Change Request
        change = models.ChangeRequest(
            title="Deploy HR DW to Production", description="Initial production deployment",
            asset_id=1, change_type="Deploy", risk_level="High",
            impact_assessment="Affects all HR reporting dashboards",
            rollback_plan="Restore from backup", requested_by=3, approval_status="Approved",
            approver_id=2, status="Completed", release_version="R1.0"
        )
        db.add(change)
        db.commit()
        print("✓ Change requests created")

        # 7. Create Strategic Data (Business Goals, Initiatives, Vendors)
        print("Seeding strategic data...")

        # Business Goals
        goals = [
            models_extended.BusinessGoal(
                goal_name="Reduce Data Access Time by 50%",
                description="Improve data platform performance to enable faster decision-making",
                owner_id=1, target_date=date(2026, 12, 31), status="Active",
                kpi_metric="Average query response time", current_value=4.2, target_value=2.1,
                priority="High"
            ),
            models_extended.BusinessGoal(
                goal_name="Achieve 100% Data Governance Compliance",
                description="Ensure all data assets comply with naming and documentation standards",
                owner_id=2, target_date=date(2026, 6, 30), status="Active",
                kpi_metric="Compliance rate", current_value=85.7, target_value=100.0,
                priority="Critical"
            ),
            models_extended.BusinessGoal(
                goal_name="Increase Self-Service Analytics Adoption",
                description="Enable business users to access and analyze data independently",
                owner_id=2, target_date=date(2026, 9, 30), status="Active",
                kpi_metric="Number of self-service users", current_value=45.0, target_value=200.0,
                priority="High"
            ),
        ]
        db.add_all(goals)
        db.commit()
        print("✓ Business goals created")

        # Strategic Initiatives
        initiatives = [
            models_extended.StrategicInitiative(
                initiative_name="Data Platform Modernization",
                description="Migrate legacy systems to cloud-based modern data platform",
                business_goal_id=1, initiative_lead_id=1,
                budget_allocated=2500000.0, budget_spent=450000.0,
                start_date=date(2026, 1, 1), target_date=date(2026, 12, 31),
                status="In Progress", expected_roi=3.5, stakeholder_count=25
            ),
            models_extended.StrategicInitiative(
                initiative_name="Data Governance Program",
                description="Implement enterprise-wide data governance framework",
                business_goal_id=2, initiative_lead_id=2,
                budget_allocated=500000.0, budget_spent=125000.0,
                start_date=date(2026, 1, 15), target_date=date(2026, 6, 30),
                status="In Progress", expected_roi=2.1, stakeholder_count=15
            ),
        ]
        db.add_all(initiatives)
        db.commit()
        print("✓ Strategic initiatives created")

        # Vendors
        vendors = [
            models_extended.Vendor(
                vendor_name="AWS", vendor_type="Cloud Provider",
                contact_name="Enterprise Support", contact_email="support@aws.amazon.com",
                status="Active", contract_start=date(2025, 1, 1), contract_end=date(2027, 12, 31),
                annual_cost=1200000.0, payment_terms="Monthly", performance_rating=5
            ),
            models_extended.Vendor(
                vendor_name="Snowflake", vendor_type="Data Warehouse",
                contact_name="Customer Success", contact_email="success@snowflake.com",
                status="Active", contract_start=date(2025, 6, 1), contract_end=date(2026, 5, 31),
                annual_cost=450000.0, payment_terms="Annual", performance_rating=5
            ),
            models_extended.Vendor(
                vendor_name="Tableau", vendor_type="Analytics Tool",
                contact_name="Account Manager", contact_email="am@tableau.com",
                status="Active", contract_start=date(2024, 3, 1), contract_end=date(2026, 2, 28),
                annual_cost=180000.0, payment_terms="Annual", performance_rating=4
            ),
        ]
        db.add_all(vendors)
        db.commit()
        print("✓ Vendors created")

        # Vendor SLAs
        slas = [
            models_extended.VendorSLA(
                vendor_id=1, sla_metric="Uptime", target_value="99.95%",
                current_value="99.97%", status="Met", measurement_period="Monthly",
                last_measured=date.today()
            ),
            models_extended.VendorSLA(
                vendor_id=2, sla_metric="Query Performance", target_value="< 3s avg",
                current_value="2.1s avg", status="Met", measurement_period="Monthly",
                last_measured=date.today()
            ),
            models_extended.VendorSLA(
                vendor_id=3, sla_metric="Support Response Time", target_value="< 4 hours",
                current_value="2.5 hours", status="Met", measurement_period="Quarterly",
                last_measured=date.today()
            ),
        ]
        db.add_all(slas)
        db.commit()
        print("✓ Vendor SLAs created")

        # Budget Allocations
        budgets = [
            models_extended.BudgetAllocation(
                fiscal_year=2026, domain_id=1, category="Infrastructure",
                allocated_amount=500000.0, spent_amount=125000.0, forecasted_spend=480000.0
            ),
            models_extended.BudgetAllocation(
                fiscal_year=2026, domain_id=2, category="Licenses",
                allocated_amount=350000.0, spent_amount=87500.0, forecasted_spend=345000.0
            ),
            models_extended.BudgetAllocation(
                fiscal_year=2026, domain_id=6, category="Cloud Services",
                allocated_amount=1200000.0, spent_amount=200000.0, forecasted_spend=1150000.0
            ),
        ]
        db.add_all(budgets)
        db.commit()
        print("✓ Budget allocations created")

        # Stakeholders
        stakeholders = [
            models_extended.Stakeholder(
                name="Sarah Williams", title="Chief Data Officer", department="Executive",
                email="swilliams@company.com", influence_level="Executive",
                engagement_level="Champion"
            ),
            models_extended.Stakeholder(
                name="Michael Brown", title="VP of Finance", department="Finance",
                email="mbrown@company.com", influence_level="High",
                engagement_level="Supporter"
            ),
            models_extended.Stakeholder(
                name="Jennifer Lee", title="Head of HR Analytics", department="Human Resources",
                email="jlee@company.com", influence_level="Medium",
                engagement_level="Supporter"
            ),
        ]
        db.add_all(stakeholders)
        db.commit()
        print("✓ Stakeholders created")

        print("\n✅ Database seeded successfully!")
        print("\n" + "="*60)
        print("  DEMO CREDENTIALS")
        print("="*60)
        print("\n  👤 Admin User:")
        print("     Username: admin")
        print("     Password: demo123")
        print("     Role: Admin (full access)")
        print("\n  👥 Other Users:")
        print("     jsmith, mjohnson, rdavis, cthomas")
        print("     Password: demo123")
        print("\n  📊 Sample Data Created:")
        print("     • 4 Roles")
        print("     • 5 Users")
        print("     • 6 Domains")
        print("     • 5 Assets (4 compliant, 1 non-compliant)")
        print("     • 3 Business Goals")
        print("     • 2 Strategic Initiatives")
        print("     • 3 Vendors with SLAs")
        print("     • 3 Budget Allocations")
        print("     • 3 Stakeholders")
        print("\n  🚀 API Documentation:")
        print("     http://localhost:8000/api/docs")
        print("="*60 + "\n")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
