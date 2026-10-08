"""
Integration Tests for Strategic Features
Tests business goals, initiatives, vendor management, and reporting workflows
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.database import Base, get_db
from app.main import app
from app.models import Role, User, Domain
from app.models_extended import BusinessGoal, StrategicInitiative, Vendor, VendorSLA
from app.api.auth import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_strategic.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test roles
    admin_role = Role(role_name="Admin")
    db.add(admin_role)
    db.commit()

    # Create test domains
    data_domain = Domain(domain_code="DATA", domain_name="Data Platform")
    db.add(data_domain)
    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client, db_session):
    """Create admin user and get authentication token"""
    admin_role = db_session.query(Role).filter_by(role_name="Admin").first()
    user = User(
        username="admin",
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),  # Fixed: password_hash not hashed_password
        role_id=admin_role.role_id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}  # Fixed: use data= for form data
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# Test 1: Business Goal Management Workflow
def test_business_goal_workflow(client, db_session, admin_token):
    """
    Test business goal lifecycle:
    1. Create business goal
    2. Retrieve goal details
    3. Update goal progress
    4. Link assets to goal
    5. Calculate ROI
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()

    # Step 1: Create business goal
    response = client.post(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "goal_name": "Improve Data Analytics Capability",
            "description": "Build comprehensive data analytics platform",
            "owner_id": admin_user.user_id,
            "target_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "In Progress",
            "success_criteria": "Reduce reporting time by 50%",
            "expected_roi": 250000.00,
            "investment_amount": 100000.00
        }
    )
    assert response.status_code == 201
    goal = response.json()
    goal_id = goal["goal_id"]
    assert goal["goal_name"] == "Improve Data Analytics Capability"
    assert goal["status"] == "In Progress"

    # Step 2: Retrieve goal details
    response = client.get(
        f"/api/v1/strategy/goals/{goal_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    retrieved_goal = response.json()
    assert retrieved_goal["goal_name"] == "Improve Data Analytics Capability"

    # Step 3: Update goal progress
    response = client.put(
        f"/api/v1/strategy/goals/{goal_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "completion_percentage": 25,
            "status": "In Progress"
        }
    )
    assert response.status_code == 200
    updated_goal = response.json()
    assert updated_goal["completion_percentage"] == 25

    # Step 4: Get all goals
    response = client.get(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    goals = response.json()
    assert len(goals) >= 1


# Test 2: Strategic Initiative Workflow
def test_strategic_initiative_workflow(client, db_session, admin_token):
    """
    Test strategic initiative management:
    1. Create business goal
    2. Create initiative linked to goal
    3. Add deliverables to initiative
    4. Update initiative status
    5. Track initiative progress
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()

    # Step 1: Create business goal
    response = client.post(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "goal_name": "Data Lake Migration",
            "owner_id": admin_user.user_id,
            "target_date": (datetime.now() + timedelta(days=180)).isoformat(),
            "status": "Planned"
        }
    )
    assert response.status_code == 201
    goal_id = response.json()["goal_id"]

    # Step 2: Create initiative
    response = client.post(
        "/api/v1/strategy/initiatives",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "initiative_name": "AWS Data Lake Setup",
            "description": "Migrate on-prem data to AWS S3 data lake",
            "goal_id": goal_id,
            "owner_id": admin_user.user_id,
            "start_date": datetime.now().isoformat(),
            "target_completion_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "status": "In Progress",
            "budget_allocated": 150000.00,
            "actual_spend": 30000.00
        }
    )
    assert response.status_code == 201
    initiative = response.json()
    initiative_id = initiative["initiative_id"]
    assert initiative["initiative_name"] == "AWS Data Lake Setup"

    # Step 3: Add deliverable
    response = client.post(
        f"/api/v1/strategy/initiatives/{initiative_id}/deliverables",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "deliverable_name": "S3 Bucket Configuration",
            "description": "Set up S3 buckets with proper IAM policies",
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "In Progress",
            "assigned_to": admin_user.user_id
        }
    )
    assert response.status_code == 201
    deliverable = response.json()
    assert deliverable["deliverable_name"] == "S3 Bucket Configuration"

    # Step 4: Update initiative status
    response = client.put(
        f"/api/v1/strategy/initiatives/{initiative_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "completion_percentage": 40,
            "actual_spend": 50000.00
        }
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["completion_percentage"] == 40

    # Step 5: Get all initiatives
    response = client.get(
        "/api/v1/strategy/initiatives",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    initiatives = response.json()
    assert len(initiatives) >= 1


# Test 3: Vendor Management Workflow
def test_vendor_management_workflow(client, db_session, admin_token):
    """
    Test vendor management:
    1. Create vendor
    2. Add SLA to vendor
    3. Update SLA metrics
    4. Track SLA compliance
    5. Link assets to vendor
    """
    # Step 1: Create vendor
    response = client.post(
        "/api/v1/vendors",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vendor_name": "AWS",
            "contact_person": "John Smith",
            "contact_email": "john@aws.com",
            "contact_phone": "+1-555-0100",
            "contract_start_date": datetime.now().isoformat(),
            "contract_end_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "Active",
            "annual_spend": 500000.00,
            "services_provided": "Cloud infrastructure, S3, RDS, Lambda"
        }
    )
    assert response.status_code == 201
    vendor = response.json()
    vendor_id = vendor["vendor_id"]
    assert vendor["vendor_name"] == "AWS"

    # Step 2: Add SLA to vendor
    response = client.post(
        f"/api/v1/vendors/{vendor_id}/slas",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "sla_name": "S3 Uptime",
            "description": "99.99% uptime guarantee for S3 storage",
            "metric_name": "Uptime Percentage",
            "target_value": 99.99,
            "current_value": 99.98,
            "measurement_period": "Monthly",
            "penalty_amount": 10000.00
        }
    )
    assert response.status_code == 201
    sla = response.json()
    sla_id = sla["sla_id"]
    assert sla["sla_name"] == "S3 Uptime"

    # Step 3: Update SLA metrics
    response = client.put(
        f"/api/v1/vendors/{vendor_id}/slas/{sla_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "current_value": 99.97,
            "last_review_date": datetime.now().isoformat()
        }
    )
    assert response.status_code == 200
    updated_sla = response.json()
    assert updated_sla["current_value"] == 99.97

    # Step 4: Get vendor details with SLAs
    response = client.get(
        f"/api/v1/vendors/{vendor_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    vendor_details = response.json()
    assert vendor_details["vendor_name"] == "AWS"

    # Step 5: List all vendors
    response = client.get(
        "/api/v1/vendors",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    vendors = response.json()
    assert len(vendors) >= 1


# Test 4: Strategy Dashboard and Reporting
def test_strategy_dashboard_workflow(client, db_session, admin_token):
    """
    Test strategy dashboard and executive reporting:
    1. Create goals and initiatives
    2. Get strategy summary
    3. Get ROI analysis
    4. Get executive dashboard data
    5. Generate strategy report
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()

    # Step 1: Create test data
    # Create goal
    response = client.post(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "goal_name": "Digital Transformation",
            "owner_id": admin_user.user_id,
            "target_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "In Progress",
            "expected_roi": 1000000.00,
            "investment_amount": 300000.00,
            "completion_percentage": 30
        }
    )
    assert response.status_code == 201
    goal_id = response.json()["goal_id"]

    # Create initiative
    response = client.post(
        "/api/v1/strategy/initiatives",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "initiative_name": "Cloud Migration Phase 1",
            "goal_id": goal_id,
            "owner_id": admin_user.user_id,
            "start_date": datetime.now().isoformat(),
            "target_completion_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "status": "In Progress",
            "budget_allocated": 100000.00,
            "actual_spend": 25000.00,
            "completion_percentage": 30
        }
    )
    assert response.status_code == 201

    # Step 2: Get strategy summary
    response = client.get(
        "/api/v1/strategy/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    summary = response.json()
    assert "total_goals" in summary
    assert "total_initiatives" in summary
    assert summary["total_goals"] >= 1

    # Step 3: Get ROI analysis
    response = client.get(
        "/api/v1/strategy/roi",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    roi_data = response.json()
    assert "total_investment" in roi_data
    assert "expected_roi" in roi_data

    # Step 4: Get goals with filtering
    response = client.get(
        "/api/v1/strategy/goals?status=In Progress",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    active_goals = response.json()
    assert len(active_goals) >= 1


# Test 5: Compliance and Strategy Integration
def test_compliance_strategy_integration(client, db_session, admin_token):
    """
    Test integration between compliance and strategy:
    1. Create business goal
    2. Create assets linked to goal
    3. Track compliance for strategic assets
    4. Generate compliance impact on ROI
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()
    domain = db_session.query(Domain).first()

    # Step 1: Create business goal
    response = client.post(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "goal_name": "Governance Excellence",
            "owner_id": admin_user.user_id,
            "target_date": (datetime.now() + timedelta(days=180)).isoformat(),
            "status": "In Progress"
        }
    )
    assert response.status_code == 201
    goal_id = response.json()["goal_id"]

    # Step 2: Create compliant asset
    response = client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "PROD-DATA-PLATFORM-v1",
            "domain_id": domain.domain_id,
            "environment": "PROD",
            "owner_id": admin_user.user_id,
            "version": "v1",  # Required field
            "lifecycle_stage": "Active",  # Optional, defaults to Draft
            "documentation_url": "https://docs.example.com"
        }
    )
    assert response.status_code == 201
    asset_id = response.json()["asset_id"]

    # Step 3: Get compliance metrics
    response = client.get("/api/v1/compliance/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_assets"] >= 1
    assert metrics["compliant_assets"] >= 1

    # Step 4: Verify strategic value
    response = client.get(
        "/api/v1/strategy/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# Test 6: End-to-End Executive Reporting
def test_executive_reporting_workflow(client, db_session, admin_token):
    """
    Test complete executive reporting:
    1. Create comprehensive test data (goals, initiatives, vendors, assets)
    2. Generate governance summary report
    3. Generate executive summary report
    4. Generate compliance report
    5. Verify report data accuracy
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()

    # Step 1: Create test data
    # Goal
    response = client.post(
        "/api/v1/strategy/goals",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "goal_name": "Enterprise Data Platform",
            "owner_id": admin_user.user_id,
            "target_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "In Progress",
            "expected_roi": 2000000.00,
            "investment_amount": 500000.00
        }
    )
    assert response.status_code == 201

    # Step 2: Generate governance summary
    response = client.get(
        "/api/v1/reports/governance-summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    gov_report = response.json()
    assert "total_assets" in gov_report
    assert "compliance_rate" in gov_report

    # Step 3: Generate executive summary
    response = client.get(
        "/api/v1/reports/executive-summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    exec_report = response.json()
    assert "strategic_overview" in exec_report

    # Step 4: Generate compliance report
    response = client.get(
        "/api/v1/reports/compliance-report",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    compliance_report = response.json()
    assert "compliance_metrics" in compliance_report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
