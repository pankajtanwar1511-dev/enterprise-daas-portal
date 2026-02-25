# Test Suite - Enterprise DaaS Governance Portal

Comprehensive test suite covering unit tests and integration tests.

## Test Structure

```
tests/
├── unit/                           # Unit tests (fast, fully mocked)
│   ├── test_auth.py               # Authentication & JWT
│   ├── test_assets.py             # Asset CRUD operations
│   ├── test_naming_validator.py   # Naming convention validation
│   ├── test_compliance.py         # Compliance metrics & violations
│   ├── test_security_middleware.py # Security middleware
│   ├── test_services.py           # Business logic services
│   └── test_phase3_integrations.py # Phase 3 features
├── integration/                    # Integration tests (database + API)
│   ├── test_api_workflows.py     # Core API workflows
│   └── test_strategic_workflows.py # Strategic feature workflows
├── conftest.py                     # Shared fixtures
└── README.md                       # This file
```

## Running Tests

### Prerequisites

```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run all tests with coverage report in terminal
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Specific Test Suites

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_security_middleware.py -v

# Specific test function
pytest tests/integration/test_api_workflows.py::test_asset_registration_workflow -v
```

### Run Tests with Output

```bash
# Show print statements and detailed output
pytest tests/ -v -s

# Show only failed tests
pytest tests/ --tb=short

# Stop on first failure
pytest tests/ -x
```

### Run Tests by Markers (if configured)

```bash
# Run only fast tests
pytest -m "fast"

# Run only slow tests
pytest -m "slow"

# Skip integration tests
pytest -m "not integration"
```

## Test Coverage

### Current Coverage Status

- **Unit Tests**: Comprehensive coverage of core modules
  - Security middleware: 15+ tests
  - Compliance module: 10+ tests
  - Authentication: Full coverage
  - Assets API: Full CRUD coverage
  - Naming validator: Comprehensive

- **Integration Tests**: End-to-end workflow coverage
  - Asset registration workflow: Complete
  - User authentication workflow: Complete
  - Change request workflow: Complete
  - Compliance violation workflow: Complete
  - Multi-asset filtering: Complete
  - Strategic features: Goals, initiatives, vendors
  - Executive reporting: Complete

### Coverage Goals

- **Target**: >80% code coverage
- **Current**: Run `pytest --cov` to check

### Generate Coverage Report

```bash
# HTML report (opens in browser)
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows

# XML report (for CI/CD)
pytest tests/ --cov=app --cov-report=xml

# Multiple formats
pytest tests/ --cov=app --cov-report=html --cov-report=xml --cov-report=term
```

## Test Database

Tests use SQLite in-memory databases for speed and isolation:

- **Unit tests**: Fully mocked, no real database
- **Integration tests**: Isolated SQLite databases (`test_*.db`)
- Each test function gets a fresh database
- Automatic cleanup after tests

## Writing New Tests

### Unit Test Example

```python
def test_my_feature(db_session):
    """Test description"""
    # Arrange
    user = User(username="test")
    db_session.add(user)
    db_session.commit()

    # Act
    result = my_function(user.user_id)

    # Assert
    assert result == expected_value
```

### Integration Test Example

```python
def test_my_workflow(client, admin_token):
    """Test complete workflow"""
    # Step 1: Create resource
    response = client.post(
        "/api/v1/resource",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test"}
    )
    assert response.status_code == 201

    # Step 2: Verify resource created
    resource_id = response.json()["id"]
    response = client.get(f"/api/v1/resource/{resource_id}")
    assert response.status_code == 200
```

## Fixtures Available

### Common Fixtures (conftest.py)

- `db_session`: Database session with test data
- `client`: FastAPI TestClient
- `admin_user`: Admin user with credentials
- `admin_token`: JWT token for admin user
- `viewer_token`: JWT token for viewer user

### Using Fixtures

```python
def test_with_fixtures(client, admin_token, db_session):
    # client: TestClient instance
    # admin_token: Valid JWT token
    # db_session: Database session with test data
    pass
```

## Debugging Tests

### Run in Debug Mode

```bash
# Show all output (print statements)
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -v --showlocals

# Drop into debugger on failure
pytest tests/ --pdb

# Drop into debugger on first failure
pytest tests/ -x --pdb
```

### Common Issues

1. **Import errors**: Ensure you're in the `backend/` directory
2. **Database errors**: Each test gets a fresh DB, check fixtures
3. **Token errors**: Use `admin_token` fixture, not hardcoded tokens
4. **Assertion failures**: Check test data setup in fixtures

## Continuous Integration

Tests run automatically on:
- Every push to `main` branch
- Every pull request
- Nightly builds

### CI Configuration

See `.github/workflows/ci.yml` for CI/CD pipeline configuration.

### CI Test Command

```bash
# Same command used in CI
pytest tests/ -v --cov=app --cov-report=xml --cov-report=term
```

## Test Performance

### Speed Optimization

- Unit tests: ~2-5 seconds total (fully mocked)
- Integration tests: ~10-30 seconds (SQLite in-memory)
- Full suite: ~30-60 seconds

### Parallel Execution (Future)

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest tests/ -n auto
```

## Best Practices

1. **Test Naming**: Use descriptive names
   - `test_asset_creation_workflow`
   - Not: `test_1`, `test_stuff`

2. **Test Structure**: Follow Arrange-Act-Assert
   ```python
   def test_feature():
       # Arrange: Set up test data
       # Act: Execute the feature
       # Assert: Verify results
   ```

3. **Test Independence**: Each test should be independent
   - Use fixtures for setup
   - Clean up in teardown
   - No shared state between tests

4. **Test Documentation**: Add docstrings
   ```python
   def test_feature():
       """
       Test that feature X does Y when Z.

       Steps:
       1. Create resource
       2. Update resource
       3. Verify changes
       """
   ```

5. **Assertions**: Be specific
   ```python
   # Good
   assert response.status_code == 201
   assert "asset_id" in response.json()

   # Bad
   assert response  # Too vague
   ```

## Troubleshooting

### Database Not Found

```bash
# Ensure you're in backend/ directory
cd backend
pytest tests/
```

### Import Errors

```bash
# Install in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Fixture Not Found

```python
# Check conftest.py has the fixture
# Check fixture scope (function, module, session)
# Check fixture is imported if from external file
```

### Slow Tests

```bash
# Identify slow tests
pytest tests/ --durations=10

# Run only fast tests
pytest tests/unit/ -v
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Last Updated**: February 25, 2026
**Test Suite Version**: v1.0
**Total Tests**: 50+ tests (unit + integration)
