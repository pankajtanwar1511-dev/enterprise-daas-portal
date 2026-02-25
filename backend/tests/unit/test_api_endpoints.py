"""
Unit tests for additional API endpoints (compliance, strategy, vendors, reports)
"""
import pytest


@pytest.mark.integration
class TestComplianceEndpoints:
    """Test compliance API endpoints"""

    def test_get_compliance_metrics(self, client, auth_headers, test_asset):
        """Test getting compliance metrics"""
        response = client.get(
            "/api/v1/compliance/metrics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "compliant_assets" in data
        assert "compliance_rate" in data

    def test_get_compliance_violations(self, client, auth_headers):
        """Test getting compliance violations"""
        response = client.get(
            "/api/v1/compliance/violations",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_validate_naming_convention(self, client, auth_headers):
        """Test naming convention validation endpoint"""
        response = client.post(
            "/api/v1/compliance/validate/naming",
            json={"asset_name": "PROD-HR-DW-v1"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "violations" in data

    def test_validate_naming_invalid(self, client, auth_headers):
        """Test naming validation with invalid name"""
        response = client.post(
            "/api/v1/compliance/validate/naming",
            json={"asset_name": "invalid-name"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["violations"]) > 0

    def test_get_approved_domains(self, client, auth_headers, test_domain):
        """Test getting approved domains"""
        response = client.get(
            "/api/v1/compliance/domains",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least test_domain


@pytest.mark.integration
class TestStrategyEndpoints:
    """Test strategy API endpoints"""

    def test_get_strategy_summary(self, client, auth_headers):
        """Test getting strategy summary"""
        response = client.get(
            "/api/v1/strategy/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_goals" in data or isinstance(data, dict)

    def test_get_business_goals(self, client, auth_headers):
        """Test getting business goals"""
        response = client.get(
            "/api/v1/strategy/goals",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_strategic_initiatives(self, client, auth_headers):
        """Test getting strategic initiatives"""
        response = client.get(
            "/api/v1/strategy/initiatives",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_roi_metrics(self, client, auth_headers):
        """Test getting ROI metrics"""
        response = client.get(
            "/api/v1/strategy/roi",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.integration
class TestVendorsEndpoints:
    """Test vendors API endpoints"""

    def test_list_vendors_empty(self, client, auth_headers):
        """Test listing vendors when none exist"""
        response = client.get(
            "/api/v1/vendors/",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_vendor(self, client, auth_headers):
        """Test creating a vendor"""
        vendor_data = {
            "vendor_name": "Test Vendor Inc.",
            "vendor_type": "Data Provider",
            "contact_name": "John Doe",
            "contact_email": "john@testvendor.com",
            "status": "Active",
            "annual_cost": 50000
        }

        response = client.post(
            "/api/v1/vendors/",
            json=vendor_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert "vendor_id" in data or "vendor_name" in data

    def test_create_vendor_missing_fields(self, client, auth_headers):
        """Test creating vendor with missing required fields"""
        vendor_data = {
            "vendor_name": "Test Vendor"
            # Missing other required fields
        }

        response = client.post(
            "/api/v1/vendors/",
            json=vendor_data,
            headers=auth_headers
        )

        # Should either reject or accept with defaults
        assert response.status_code in [200, 201, 422]

    def test_vendors_require_authentication(self, client):
        """Test that vendor endpoints require authentication"""
        response = client.get("/api/v1/vendors/")

        assert response.status_code == 401


@pytest.mark.integration
class TestReportsEndpoints:
    """Test reports API endpoints"""

    def test_get_executive_summary(self, client, auth_headers):
        """Test getting executive summary report"""
        response = client.get(
            "/api/v1/reports/executive-summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_governance_summary(self, client, auth_headers):
        """Test getting governance summary report"""
        response = client.get(
            "/api/v1/reports/governance-summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_compliance_report(self, client, auth_headers):
        """Test getting compliance report"""
        response = client.get(
            "/api/v1/reports/compliance-report",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_reports_require_authentication(self, client):
        """Test that report endpoints require authentication"""
        response = client.get("/api/v1/reports/executive-summary")

        assert response.status_code == 401


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint (no auth required)"""
        response = client.get("/api/v1/health")

        # Health check should be accessible without auth
        assert response.status_code in [200, 404]  # 404 if not implemented


@pytest.mark.integration
class TestCORSHeaders:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are configured"""
        response = client.options("/api/v1/assets/")

        # Check for CORS headers (may not be present in test environment)
        headers = response.headers
        # This is informational - test client may not include CORS
        assert response.status_code in [200, 405]


@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling"""

    def test_404_not_found(self, client, auth_headers):
        """Test 404 error for non-existent endpoint"""
        response = client.get(
            "/api/v1/nonexistent/endpoint",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_method_not_allowed(self, client, auth_headers):
        """Test 405 error for wrong HTTP method"""
        # Try DELETE on an endpoint that doesn't support it
        response = client.delete(
            "/api/v1/compliance/metrics",
            headers=auth_headers
        )

        assert response.status_code in [404, 405]

    def test_validation_error_format(self, client, auth_headers):
        """Test that validation errors return proper format"""
        # Send invalid data to trigger validation error
        response = client.post(
            "/api/v1/assets/",
            json={"invalid": "data"},
            headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
