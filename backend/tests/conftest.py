"""
Pytest configuration and fixtures
"""
# Unregister conflicting ROS pytest plugins before pytest loads them
import sys
import pytest

# Block ROS pytest plugins from loading
pytest_plugins_to_block = [
    'launch_testing_ros_pytest_entrypoint',
    'rostest',
    'launch_testing',
    'ament_copyright',
    'ament_flake8',
    'ament_lint',
    'ament_pep257',
    'ament_xmllint',
]

for plugin in pytest_plugins_to_block:
    if plugin in sys.modules:
        del sys.modules[plugin]

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models
from app.auth import create_access_token, get_password_hash


# Test database setup (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)  # Fixed: Remove keyword argument
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user"""
    # Create role first
    role = models.Role(
        role_name="Admin",
        description="Administrator",
        permissions="{}"
    )
    db.add(role)
    db.flush()

    # Create user
    user = models.User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        role_id=role.role_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user):
    """Generate authentication token for test user"""
    token = create_access_token(data={"sub": test_user.username})
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Generate authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_domain(db):
    """Create a test domain"""
    domain = models.Domain(
        domain_code="TEST",
        domain_name="Test Domain",
        description="Test domain for testing",
        is_active=True
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


@pytest.fixture(scope="function")
def test_asset(db, test_user, test_domain):
    """Create a test asset"""
    asset = models.Asset(
        asset_name="PROD-TEST-SYS-v1",
        domain_id=test_domain.domain_id,
        environment="PROD",
        owner_id=test_user.user_id,
        version="v1.0",
        lifecycle_stage="Active",
        description="Test asset",
        business_justification="Testing",
        naming_compliant=True,
        created_by=test_user.user_id
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@pytest.fixture(scope="function")
def sample_assets_data():
    """Sample asset data for testing"""
    return [
        {
            "asset_name": "PROD-HR-DW-v1",
            "environment": "PROD",
            "version": "v1.0",
            "lifecycle_stage": "Active",
            "description": "HR Data Warehouse",
            "business_justification": "HR analytics"
        },
        {
            "asset_name": "QA-FIN-ETL-v2",
            "environment": "QA",
            "version": "v2.0",
            "lifecycle_stage": "Testing",
            "description": "Finance ETL",
            "business_justification": "Financial reporting"
        }
    ]
