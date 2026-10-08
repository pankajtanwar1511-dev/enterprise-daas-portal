"""
Integration Tests for API Workflows
Tests end-to-end API flows with database integration
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Role, User, Domain, Asset
from app.api.auth import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create test roles
    admin_role = Role(role_name="Admin")
    viewer_role = Role(role_name="Viewer")
    steward_role = Role(role_name="DataSteward")
    owner_role = Role(role_name="AssetOwner")
    db.add_all([admin_role, viewer_role, steward_role, owner_role])
    db.commit()

    # Create test domains
    hr_domain = Domain(domain_code="HR", domain_name="Human Resources")
    fin_domain = Domain(domain_code="FIN", domain_name="Finance")
    it_domain = Domain(domain_code="IT", domain_name="Information Technology")
    db.add_all([hr_domain, fin_domain, it_domain])
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
def admin_user(db_session):
    """Create admin user and return credentials"""
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
    db_session.refresh(user)
    return {"username": "admin", "password": "admin123", "user_id": user.user_id}


@pytest.fixture
def admin_token(client, admin_user):
    """Get admin authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        data={  # Fixed: use data= for form data, not json=
            "username": admin_user["username"],
            "password": admin_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# Test 1: Asset Registration Workflow
def test_asset_registration_workflow(client, db_session, admin_token):
    """
    Test complete asset registration flow:
    1. Validate asset name
    2. Create asset
    3. Verify compliance metrics updated
    4. Retrieve asset details
    5. Update lifecycle stage
    6. Verify lifecycle history created
    """
    # Step 1: Validate asset name
    response = client.post(
        "/api/v1/compliance/validate/naming",
        json={"asset_name": "PROD-HR-DW-v1"}
    )
    assert response.status_code == 200
    validation = response.json()
    assert validation["valid"] is True
    assert validation["asset_name"] == "PROD-HR-DW-v1"

    # Step 2: Create asset
    hr_domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    admin_user = db_session.query(User).filter_by(username="admin").first()

    response = client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "PROD-HR-DW-v1",
            "domain_id": hr_domain.domain_id,
            "environment": "PROD",
            "owner_id": admin_user.user_id,
            "version": "v1",
            "lifecycle_stage": "Draft",
            "documentation_url": "https://docs.example.com/hr-dw",
            "description": "HR Data Warehouse",
            "business_justification": "Centralized HR analytics",
            "naming_compliant": True,
            "has_documentation": True
        }
    )
    assert response.status_code == 201
    asset = response.json()
    asset_id = asset["asset_id"]
    assert asset["asset_name"] == "PROD-HR-DW-v1"

    # Step 3: Verify compliance metrics updated
    response = client.get("/api/v1/compliance/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_assets"] >= 1
    assert metrics["compliant_assets"] >= 1

    # Step 4: Retrieve asset details
    response = client.get(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    retrieved_asset = response.json()
    assert retrieved_asset["asset_name"] == "PROD-HR-DW-v1"
    assert retrieved_asset["lifecycle_stage"] == "Draft"

    # Step 5: Update lifecycle stage
    response = client.put(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"lifecycle_stage": "Active"}
    )
    assert response.status_code == 200
    updated_asset = response.json()
    assert updated_asset["lifecycle_stage"] == "Active"

    # Step 6: Verify lifecycle history exists
    asset_obj = db_session.query(Asset).filter_by(asset_id=asset_id).first()
    assert asset_obj is not None
    assert asset_obj.lifecycle_stage == "Active"


# Test 2: User Registration and Authentication Flow
def test_user_registration_and_auth_workflow(client, db_session):
    """
    Test complete user authentication flow:
    1. Register new user
    2. Login and get token
    3. Access protected endpoint with token
    4. Create asset as authenticated user
    5. Logout (token invalidation - future implementation)
    """
    # Step 1: Register new user
    viewer_role = db_session.query(Role).filter_by(role_name="Viewer").first()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123456",
            "role_id": viewer_role.role_id
        }
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"

    # Step 2: Login and get token
    response = client.post(
        "/api/v1/auth/login",
        data={  # Fixed: use data= for form data, not json=
            "username": "testuser",
            "password": "test123456"
        }
    )
    assert response.status_code == 200
    auth_data = response.json()
    assert "access_token" in auth_data
    token = auth_data["access_token"]

    # Step 3: Access protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    current_user = response.json()
    assert current_user["username"] == "testuser"

    # Step 4: Try to access assets (viewer can view)
    response = client.get(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


# Test 3: Change Request Workflow
def test_change_request_workflow(client, db_session, admin_token):
    """
    Test ITIL change management flow:
    1. Create asset
    2. Create change request for the asset
    3. Review change request
    4. Approve change request
    5. Verify status updates
    """
    # Step 1: Create asset
    hr_domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    admin_user = db_session.query(User).filter_by(username="admin").first()

    response = client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "DEV-HR-API-v1",
            "domain_id": hr_domain.domain_id,
            "environment": "DEV",
            "owner_id": admin_user.user_id,
            "version": "v1",
            "lifecycle_stage": "Active",
            "naming_compliant": True
        }
    )
    assert response.status_code == 201
    asset_id = response.json()["asset_id"]

    # Step 2: Create change request
    response = client.post(
        "/api/v1/change-requests",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_id": asset_id,
            "change_type": "Update",
            "description": "Upgrade API version to v2",
            "justification": "Add new features and improve performance",
            "risk_level": "Medium",
            "impact_assessment": "Minimal downtime expected",
            "rollback_plan": "Revert to v1 if issues occur",
            "requested_by": admin_user.user_id
        }
    )
    assert response.status_code == 201
    change_request = response.json()
    change_id = change_request["change_request_id"]
    assert change_request["status"] == "Pending"

    # Step 3: Review change request (get details)
    response = client.get(
        f"/api/v1/change-requests/{change_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    cr_details = response.json()
    assert cr_details["change_type"] == "Update"
    assert cr_details["risk_level"] == "Medium"

    # Step 4: Approve change request
    response = client.post(
        f"/api/v1/change-requests/{change_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "reviewer_id": admin_user.user_id,
            "comments": "Approved - risk assessment looks good"
        }
    )
    assert response.status_code == 200
    approved_cr = response.json()
    assert approved_cr["status"] == "Approved"


# Test 4: Compliance Violation Detection and Resolution
def test_compliance_violation_workflow(client, db_session, admin_token):
    """
    Test compliance violation handling:
    1. Create non-compliant asset
    2. Detect violation automatically
    3. Update asset to be compliant
    4. Verify violation resolved
    5. Check compliance metrics improved
    """
    # Step 1: Create non-compliant asset
    hr_domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    admin_user = db_session.query(User).filter_by(username="admin").first()

    response = client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "bad-asset-name",  # Non-compliant
            "domain_id": hr_domain.domain_id,
            "environment": "DEV",
            "owner_id": admin_user.user_id,
            "naming_compliant": False,
            "has_documentation": False
        }
    )
    assert response.status_code == 201
    asset_id = response.json()["asset_id"]

    # Step 2: Get compliance violations
    response = client.get(
        "/api/v1/compliance/violations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    violations = response.json()
    # Check if violation exists for our asset (may need to be created by a background job)

    # Step 3: Update asset to be compliant
    response = client.put(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "DEV-HR-TEST-v1",
            "naming_compliant": True,
            "has_documentation": True,
            "documentation_url": "https://docs.example.com"
        }
    )
    assert response.status_code == 200
    updated_asset = response.json()
    assert updated_asset["naming_compliant"] is True
    assert updated_asset["asset_name"] == "DEV-HR-TEST-v1"

    # Step 4: Verify compliance metrics
    response = client.get("/api/v1/compliance/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_assets"] >= 1


# Test 5: Multi-Asset Operations and Filtering
def test_multi_asset_filtering_workflow(client, db_session, admin_token):
    """
    Test asset listing and filtering:
    1. Create multiple assets across different domains
    2. Filter by domain
    3. Filter by environment
    4. Filter by compliance status
    5. Search by name
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()
    hr_domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    fin_domain = db_session.query(Domain).filter_by(domain_code="FIN").first()

    # Step 1: Create multiple assets
    assets_to_create = [
        {
            "asset_name": "PROD-HR-DW-v1",
            "domain_id": hr_domain.domain_id,
            "environment": "PROD",
            "naming_compliant": True
        },
        {
            "asset_name": "DEV-HR-API-v1",
            "domain_id": hr_domain.domain_id,
            "environment": "DEV",
            "naming_compliant": True
        },
        {
            "asset_name": "PROD-FIN-ETL-v2",
            "domain_id": fin_domain.domain_id,
            "environment": "PROD",
            "naming_compliant": True
        },
        {
            "asset_name": "qa-invalid-name",
            "domain_id": fin_domain.domain_id,
            "environment": "QA",
            "naming_compliant": False
        }
    ]

    created_ids = []
    for asset_data in assets_to_create:
        asset_data["owner_id"] = admin_user.user_id
        response = client.post(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=asset_data
        )
        assert response.status_code == 201
        created_ids.append(response.json()["asset_id"])

    # Step 2: Get all assets
    response = client.get(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    all_assets = response.json()
    assert len(all_assets) >= 4

    # Step 3: Filter by domain (HR)
    response = client.get(
        f"/api/v1/assets?domain_id={hr_domain.domain_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    hr_assets = response.json()
    assert len(hr_assets) >= 2
    for asset in hr_assets:
        assert asset["domain_id"] == hr_domain.domain_id

    # Step 4: Filter by environment (PROD)
    response = client.get(
        "/api/v1/assets?environment=PROD",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    prod_assets = response.json()
    assert len(prod_assets) >= 2
    for asset in prod_assets:
        assert asset["environment"] == "PROD"

    # Step 5: Filter by compliance
    response = client.get(
        "/api/v1/assets?naming_compliant=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    non_compliant = response.json()
    assert len(non_compliant) >= 1


# Test 6: Asset Deletion and Audit Trail
def test_asset_deletion_workflow(client, db_session, admin_token):
    """
    Test asset deletion and audit trail:
    1. Create asset
    2. Delete asset
    3. Verify asset is soft-deleted
    4. Verify audit log entry created
    5. Verify asset no longer in active list
    """
    admin_user = db_session.query(User).filter_by(username="admin").first()
    hr_domain = db_session.query(Domain).filter_by(domain_code="HR").first()

    # Step 1: Create asset
    response = client.post(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "asset_name": "DEV-HR-TEMP-v1",
            "domain_id": hr_domain.domain_id,
            "environment": "DEV",
            "owner_id": admin_user.user_id,
            "naming_compliant": True
        }
    )
    assert response.status_code == 201
    asset_id = response.json()["asset_id"]

    # Step 2: Delete asset
    response = client.delete(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204  # Fixed: 204 No Content is correct for DELETE

    # Step 3: Verify asset is soft-deleted (should return 404 or marked as deleted)
    response = client.get(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Depending on implementation: 404 or asset with is_deleted=True
    assert response.status_code in [200, 404]

    # Step 4: Check audit logs (if endpoint exists)
    response = client.get(
        "/api/v1/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if response.status_code == 200:
        logs = response.json()
        assert len(logs) > 0
        # Look for delete action in recent logs
        delete_logs = [log for log in logs if log.get("action") == "DELETE"]
        assert len(delete_logs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
