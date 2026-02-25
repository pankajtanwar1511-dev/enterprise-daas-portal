"""
Unit tests for assets CRUD operations
"""
import pytest
from datetime import datetime


@pytest.mark.integration
class TestAssetsListEndpoint:
    """Test asset listing endpoint"""

    def test_list_assets_empty(self, client, auth_headers):
        """Test listing assets when none exist"""
        response = client.get("/api/v1/assets/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_assets_with_data(self, client, auth_headers, test_asset):
        """Test listing assets when assets exist"""
        response = client.get("/api/v1/assets/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["asset_name"] == "PROD-TEST-SYS-v1"

    def test_list_assets_requires_authentication(self, client):
        """Test that listing assets requires authentication"""
        response = client.get("/api/v1/assets/")

        assert response.status_code == 401


@pytest.mark.integration
class TestAssetCreation:
    """Test asset creation endpoint"""

    def test_create_asset_success(self, client, auth_headers, test_domain):
        """Test successful asset creation"""
        asset_data = {
            "asset_name": "PROD-HR-DW-v1",
            "domain_id": test_domain.domain_id,
            "environment": "PROD",
            "owner_id": 1,
            "version": "v1.0",
            "lifecycle_stage": "Active",
            "description": "HR Data Warehouse",
            "business_justification": "HR analytics and reporting"
        }

        response = client.post(
            "/api/v1/assets/",
            json=asset_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["asset_name"] == "PROD-HR-DW-v1"
        assert data["environment"] == "PROD"
        assert data["naming_compliant"] is True
        assert "asset_id" in data

    def test_create_asset_non_compliant_name(self, client, auth_headers, test_domain):
        """Test creating asset with non-compliant name"""
        asset_data = {
            "asset_name": "invalid-name",
            "domain_id": test_domain.domain_id,
            "environment": "PROD",
            "owner_id": 1,
            "version": "v1.0",
            "lifecycle_stage": "Active",
            "description": "Test asset",
            "business_justification": "Testing"
        }

        response = client.post(
            "/api/v1/assets/",
            json=asset_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["naming_compliant"] is False

    def test_create_asset_missing_required_fields(self, client, auth_headers):
        """Test creating asset with missing required fields"""
        asset_data = {
            "asset_name": "PROD-HR-DW-v1"
            # Missing other required fields
        }

        response = client.post(
            "/api/v1/assets/",
            json=asset_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_create_asset_requires_authentication(self, client, test_domain):
        """Test that creating asset requires authentication"""
        asset_data = {
            "asset_name": "PROD-HR-DW-v1",
            "domain_id": test_domain.domain_id,
            "environment": "PROD",
            "owner_id": 1,
            "version": "v1.0",
            "lifecycle_stage": "Active",
            "description": "Test",
            "business_justification": "Test"
        }

        response = client.post("/api/v1/assets/", json=asset_data)

        assert response.status_code == 401


@pytest.mark.integration
class TestAssetRetrieval:
    """Test asset retrieval endpoint"""

    def test_get_asset_by_id_success(self, client, auth_headers, test_asset):
        """Test successful asset retrieval by ID"""
        response = client.get(
            f"/api/v1/assets/{test_asset.asset_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["asset_id"] == test_asset.asset_id
        assert data["asset_name"] == test_asset.asset_name

    def test_get_asset_not_found(self, client, auth_headers):
        """Test getting non-existent asset"""
        response = client.get(
            "/api/v1/assets/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_asset_requires_authentication(self, client, test_asset):
        """Test that getting asset requires authentication"""
        response = client.get(f"/api/v1/assets/{test_asset.asset_id}")

        assert response.status_code == 401


@pytest.mark.integration
class TestAssetUpdate:
    """Test asset update endpoint"""

    def test_update_asset_success(self, client, auth_headers, test_asset):
        """Test successful asset update"""
        update_data = {
            "description": "Updated description",
            "lifecycle_stage": "Deprecated"
        }

        response = client.put(
            f"/api/v1/assets/{test_asset.asset_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["lifecycle_stage"] == "Deprecated"

    def test_update_asset_not_found(self, client, auth_headers):
        """Test updating non-existent asset"""
        update_data = {"description": "Updated"}

        response = client.put(
            "/api/v1/assets/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_asset_partial_update(self, client, auth_headers, test_asset):
        """Test partial asset update"""
        original_name = test_asset.asset_name

        update_data = {"description": "Only description changed"}

        response = client.put(
            f"/api/v1/assets/{test_asset.asset_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Only description changed"
        assert data["asset_name"] == original_name  # Unchanged

    def test_update_asset_requires_authentication(self, client, test_asset):
        """Test that updating asset requires authentication"""
        update_data = {"description": "Updated"}

        response = client.put(
            f"/api/v1/assets/{test_asset.asset_id}",
            json=update_data
        )

        assert response.status_code == 401


@pytest.mark.integration
class TestAssetDeletion:
    """Test asset deletion endpoint"""

    def test_delete_asset_success(self, client, auth_headers, test_asset, db):
        """Test successful asset deletion"""
        asset_id = test_asset.asset_id

        response = client.delete(
            f"/api/v1/assets/{asset_id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify asset is deleted
        get_response = client.get(
            f"/api/v1/assets/{asset_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_asset_not_found(self, client, auth_headers):
        """Test deleting non-existent asset"""
        response = client.delete(
            "/api/v1/assets/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_asset_requires_authentication(self, client, test_asset):
        """Test that deleting asset requires authentication"""
        response = client.delete(f"/api/v1/assets/{test_asset.asset_id}")

        assert response.status_code == 401


@pytest.mark.integration
class TestAssetFiltering:
    """Test asset filtering and search"""

    def test_filter_assets_by_environment(self, client, auth_headers, test_asset, test_user, test_domain, db):
        """Test filtering assets by environment"""
        from app import models

        # Create additional assets with different environments
        qa_asset = models.Asset(
            asset_name="QA-TEST-SYS-v1",
            domain_id=test_domain.domain_id,
            environment="QA",
            owner_id=test_user.user_id,
            version="v1.0",
            lifecycle_stage="Active",
            description="QA asset",
            business_justification="Testing",
            naming_compliant=True,
            created_by=test_user.user_id
        )
        db.add(qa_asset)
        db.commit()

        # Filter by PROD
        response = client.get(
            "/api/v1/assets/?environment=PROD",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(asset["environment"] == "PROD" for asset in data)

    def test_filter_assets_by_lifecycle_stage(self, client, auth_headers, test_asset, test_user, test_domain, db):
        """Test filtering assets by lifecycle stage"""
        from app import models

        # Create deprecated asset
        deprecated_asset = models.Asset(
            asset_name="PROD-OLD-SYS-v1",
            domain_id=test_domain.domain_id,
            environment="PROD",
            owner_id=test_user.user_id,
            version="v1.0",
            lifecycle_stage="Deprecated",
            description="Old asset",
            business_justification="Testing",
            naming_compliant=True,
            created_by=test_user.user_id
        )
        db.add(deprecated_asset)
        db.commit()

        # Filter by Active
        response = client.get(
            "/api/v1/assets/?lifecycle_stage=Active",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(asset["lifecycle_stage"] == "Active" for asset in data)
