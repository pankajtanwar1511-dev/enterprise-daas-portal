"""
Unit tests for Compliance Module
Tests compliance metrics, validation, and reporting
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Asset, Domain, ComplianceViolation, ComplianceMetric, Role, User
from app.services.naming_validator import NamingValidator


# Test database setup
@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test roles
    admin_role = Role(role_name="Admin", description="Administrator", permissions="{}")
    viewer_role = Role(role_name="Viewer", description="Viewer", permissions="{}")
    session.add_all([admin_role, viewer_role])
    session.commit()

    # Create test user
    user = User(
        username="test_user",
        email="test@example.com",
        password_hash="hashed",
        role_id=admin_role.role_id
    )
    session.add(user)
    session.commit()

    # Create test domains
    hr_domain = Domain(domain_code="HR", domain_name="Human Resources")
    fin_domain = Domain(domain_code="FIN", domain_name="Finance")
    it_domain = Domain(domain_code="IT", domain_name="Information Technology")
    sales_domain = Domain(domain_code="SALES", domain_name="Sales")
    session.add_all([hr_domain, fin_domain, it_domain, sales_domain])
    session.commit()

    yield session

    session.close()


def test_naming_validator_valid_names(db_session):
    """Test naming validator accepts valid asset names"""
    valid_names = [
        "PROD-HR-DW-v1",
        "DEV-FIN-ETL-v2.1",
        "QA-IT-API-v1.0",
        "UAT-SALES-DASHBOARD-v3",
    ]

    for name in valid_names:
        is_valid, errors = NamingValidator.validate(name, db_session)
        assert is_valid is True, f"Name {name} should be valid"
        assert len(errors) == 0


def test_naming_validator_invalid_names(db_session):
    """Test naming validator rejects invalid asset names"""
    invalid_names = [
        "prod-hr-dw-v1",  # lowercase
        "PROD-INVALID-DW-v1",  # invalid domain
        "PROD-HR-DW-1",  # missing 'v' prefix
        "HR-DW-v1",  # missing environment
        "PROD-HR-v1",  # missing system name
        "PROD_HR_DW_v1",  # wrong separator
    ]

    for name in invalid_names:
        is_valid, errors = NamingValidator.validate(name, db_session)
        assert is_valid is False, f"Name {name} should be invalid"
        assert len(errors) > 0


def test_create_compliant_asset(db_session):
    """Test creating compliant asset"""
    domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    user = db_session.query(User).first()

    asset = Asset(
        asset_name="PROD-HR-DW-v1",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        lifecycle_stage="Active",
        documentation_url="https://docs.example.com",
        description="HR Data Warehouse",
        business_justification="HR data analytics",
        naming_compliant=True,
        created_by=user.user_id
    )

    db_session.add(asset)
    db_session.commit()

    assert asset.asset_id is not None
    assert asset.naming_compliant is True
    assert asset.documentation_url is not None


def test_create_noncompliant_asset(db_session):
    """Test creating non-compliant asset"""
    domain = db_session.query(Domain).filter_by(domain_code="FIN").first()
    user = db_session.query(User).first()

    asset = Asset(
        asset_name="finance-warehouse",  # Non-compliant name
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        lifecycle_stage="Active",
        naming_compliant=False,
        created_by=user.user_id
    )

    db_session.add(asset)
    db_session.commit()

    assert asset.asset_id is not None
    assert asset.naming_compliant is False
    assert asset.documentation_url is None


def test_compliance_violation_tracking(db_session):
    """Test compliance violation creation and tracking"""
    domain = db_session.query(Domain).filter_by(domain_code="IT").first()
    user = db_session.query(User).first()

    # Create non-compliant asset
    asset = Asset(
        asset_name="it-api-service",
        domain_id=domain.domain_id,
        environment="DEV",
        owner_id=user.user_id,
        version="v1",
        lifecycle_stage="Active",
        naming_compliant=False,
        created_by=user.user_id
    )
    db_session.add(asset)
    db_session.commit()

    # Create violation record
    violation = ComplianceViolation(
        asset_id=asset.asset_id,
        violation_type="naming_convention",
        severity="Medium",
        description="Asset name does not follow ENV-DOMAIN-SYSTEM-VERSION format",
        detected_at=datetime.utcnow()
    )
    db_session.add(violation)
    db_session.commit()

    assert violation.violation_id is not None
    assert violation.asset_id == asset.asset_id
    assert violation.resolved_at is None
    assert violation.severity == "Medium"


def test_compliance_metrics_calculation(db_session):
    """Test compliance metrics calculation"""
    domain = db_session.query(Domain).filter_by(domain_code="HR").first()
    user = db_session.query(User).first()

    # Create mix of compliant and non-compliant assets
    compliant_asset1 = Asset(
        asset_name="PROD-HR-DW-v1",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        naming_compliant=True,
        created_by=user.user_id,
        lifecycle_stage="Active"
    )

    compliant_asset2 = Asset(
        asset_name="PROD-HR-ETL-v1",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        naming_compliant=True,
        created_by=user.user_id,
        lifecycle_stage="Active"
    )

    noncompliant_asset = Asset(
        asset_name="hr-api",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        naming_compliant=False,
        lifecycle_stage="Active",
        created_by=user.user_id
    )

    db_session.add_all([compliant_asset1, compliant_asset2, noncompliant_asset])
    db_session.commit()

    # Calculate metrics
    total_assets = db_session.query(Asset).count()
    compliant_assets = db_session.query(Asset).filter(Asset.naming_compliant == True).count()
    compliance_rate = (compliant_assets / total_assets * 100) if total_assets > 0 else 0

    assert total_assets == 3
    assert compliant_assets == 2
    assert compliance_rate == pytest.approx(66.67, 0.01)


def test_compliance_metric_storage(db_session):
    """Test storing compliance metrics over time"""
    now = datetime.utcnow()

    # Store metrics for different time periods
    metric1 = ComplianceMetric(
        metric_date=now - timedelta(days=7),
        total_assets=100,
        compliant_assets=85,
        compliance_rate=85.0,
        missing_documentation=10,
        version_conflicts=15,
        pending_changes=5
    )

    metric2 = ComplianceMetric(
        metric_date=now,
        total_assets=105,
        compliant_assets=95,
        compliance_rate=90.48,
        missing_documentation=5,
        version_conflicts=10,
        pending_changes=3
    )

    db_session.add_all([metric1, metric2])
    db_session.commit()

    # Query metrics
    metrics = db_session.query(ComplianceMetric).order_by(ComplianceMetric.metric_date).all()

    assert len(metrics) == 2
    assert metrics[0].compliance_rate == 85.0
    assert metrics[1].compliance_rate == 90.48
    # Check improvement
    assert metrics[1].compliance_rate > metrics[0].compliance_rate


def test_violation_resolution(db_session):
    """Test resolving compliance violations"""
    domain = db_session.query(Domain).first()
    user = db_session.query(User).first()

    asset = Asset(
        asset_name="invalid-name",
        domain_id=domain.domain_id,
        environment="DEV",
        owner_id=user.user_id,
        version="v1",
        naming_compliant=False,
        lifecycle_stage="Active",
        created_by=user.user_id
    )
    db_session.add(asset)
    db_session.commit()

    # Create violation
    violation = ComplianceViolation(
        asset_id=asset.asset_id,
        violation_type="naming_convention",
        severity="High",
        description="Invalid naming format",
        detected_at=datetime.utcnow()
    )
    db_session.add(violation)
    db_session.commit()

    # Resolve violation
    asset.asset_name = "DEV-HR-API-v1"
    asset.naming_compliant = True

    violation.resolved_at = datetime.utcnow()
    violation.resolved_by = user.user_id
    violation.resolution_notes = "Asset renamed to comply with naming convention"

    db_session.commit()

    assert asset.naming_compliant is True
    assert violation.resolved_at is not None
    assert violation.resolved_by == user.user_id


def test_missing_documentation_detection(db_session):
    """Test detection of assets with missing documentation"""
    domain = db_session.query(Domain).first()
    user = db_session.query(User).first()

    # Asset with documentation
    with_docs = Asset(
        asset_name="PROD-HR-DW-v1",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        documentation_url="https://docs.example.com/hr-dw",
        created_by=user.user_id,
        lifecycle_stage="Active"
    )

    # Asset without documentation
    without_docs = Asset(
        asset_name="PROD-HR-API-v1",
        domain_id=domain.domain_id,
        environment="PROD",
        owner_id=user.user_id,
        version="v1",
        documentation_url=None,
        created_by=user.user_id,
        lifecycle_stage="Active"
    )

    db_session.add_all([with_docs, without_docs])
    db_session.commit()

    # Query assets missing documentation
    missing_docs = db_session.query(Asset).filter(Asset.documentation_url == None).all()

    assert len(missing_docs) == 1
    assert missing_docs[0].asset_name == "PROD-HR-API-v1"


def test_lifecycle_stage_compliance(db_session):
    """Test that lifecycle stages are tracked correctly"""
    domain = db_session.query(Domain).first()
    user = db_session.query(User).first()

    valid_stages = ["Draft", "Active", "Deprecated", "Retired"]

    for stage in valid_stages:
        asset = Asset(
            asset_name=f"PROD-HR-{stage}-v1",
            domain_id=domain.domain_id,
            environment="PROD",
            owner_id=user.user_id,
            version="v1",
            lifecycle_stage=stage,
            naming_compliant=True,
            created_by=user.user_id
        )
        db_session.add(asset)

    db_session.commit()

    # Query by lifecycle stage
    active_assets = db_session.query(Asset).filter(Asset.lifecycle_stage == "Active").count()

    assert active_assets == 1  # Only one asset has lifecycle_stage == "Active"


def test_environment_validation(db_session):
    """Test environment validation"""
    valid_environments = ["DEV", "QA", "UAT", "PROD"]
    domain = db_session.query(Domain).first()
    user = db_session.query(User).first()

    for env in valid_environments:
        asset = Asset(
            asset_name=f"{env}-HR-DW-v1",
            domain_id=domain.domain_id,
            environment=env,
            owner_id=user.user_id,
            version="v1",
            naming_compliant=True,
            lifecycle_stage="Active",
            created_by=user.user_id
        )
        db_session.add(asset)

    db_session.commit()

    # Verify all environments
    for env in valid_environments:
        count = db_session.query(Asset).filter(Asset.environment == env).count()
        assert count >= 1, f"Environment {env} should have assets"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
