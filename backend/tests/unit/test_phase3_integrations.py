"""
Unit tests for Phase 3 enterprise integration features (webhooks and API keys)
"""
import pytest
import hashlib
from app.models_integrations import Webhook, APIKey


@pytest.mark.integration
class TestWebhookCreation:
    """Test webhook creation and management"""

    def test_create_webhook_success(self, client, auth_headers):
        """Test successful webhook creation"""
        webhook_data = {
            "name": "Test Webhook",
            "url": "https://webhook.site/test",
            "events": ["asset.created", "asset.updated"],
            "retry_count": 3,
            "timeout_seconds": 10
        }

        response = client.post(
            "/api/v1/webhooks/",
            json=webhook_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Webhook"
        assert data["url"] == "https://webhook.site/test"
        assert data["active"] is True
        assert "webhook_id" in data
        assert "secret" in data  # Secret should be returned

    def test_create_webhook_missing_required_fields(self, client, auth_headers):
        """Test webhook creation with missing fields"""
        webhook_data = {
            "name": "Test Webhook"
            # Missing url and events
        }

        response = client.post(
            "/api/v1/webhooks/",
            json=webhook_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_webhook_invalid_url(self, client, auth_headers):
        """Test webhook creation with invalid URL"""
        webhook_data = {
            "name": "Test Webhook",
            "url": "not-a-url",
            "events": ["asset.created"]
        }

        response = client.post(
            "/api/v1/webhooks/",
            json=webhook_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_webhook_requires_authentication(self, client):
        """Test that creating webhook requires authentication"""
        webhook_data = {
            "name": "Test Webhook",
            "url": "https://webhook.site/test",
            "events": ["asset.created"]
        }

        response = client.post("/api/v1/webhooks/", json=webhook_data)

        assert response.status_code == 401


@pytest.mark.integration
class TestWebhookRetrieval:
    """Test webhook retrieval endpoints"""

    def test_list_webhooks_empty(self, client, auth_headers):
        """Test listing webhooks when none exist"""
        response = client.get("/api/v1/webhooks/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_webhooks_with_data(self, client, auth_headers, db, test_user):
        """Test listing webhooks"""
        # Create a webhook
        webhook = Webhook(
            name="Test Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.created"],
            active=True,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()

        response = client.get("/api/v1/webhooks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Test Webhook"

    def test_get_webhook_by_id(self, client, auth_headers, db, test_user):
        """Test getting webhook by ID"""
        webhook = Webhook(
            name="Test Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.created"],
            active=True,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        response = client.get(
            f"/api/v1/webhooks/{webhook.webhook_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["webhook_id"] == webhook.webhook_id

    def test_get_webhook_not_found(self, client, auth_headers):
        """Test getting non-existent webhook"""
        response = client.get("/api/v1/webhooks/99999", headers=auth_headers)

        assert response.status_code == 404


@pytest.mark.integration
class TestWebhookUpdate:
    """Test webhook update endpoints"""

    def test_update_webhook_success(self, client, auth_headers, db, test_user):
        """Test successful webhook update"""
        webhook = Webhook(
            name="Test Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.created"],
            active=True,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        update_data = {
            "name": "Updated Webhook",
            "events": ["asset.created", "asset.updated", "asset.deleted"]
        }

        response = client.put(
            f"/api/v1/webhooks/{webhook.webhook_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Webhook"
        assert len(data["events"]) == 3

    def test_delete_webhook_success(self, client, auth_headers, db, test_user):
        """Test successful webhook deletion"""
        webhook = Webhook(
            name="Test Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.created"],
            active=True,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        response = client.delete(
            f"/api/v1/webhooks/{webhook.webhook_id}",
            headers=auth_headers
        )

        assert response.status_code == 200


@pytest.mark.integration
class TestAPIKeyGeneration:
    """Test API key generation and management"""

    def test_generate_api_key_success(self, client, auth_headers):
        """Test successful API key generation"""
        key_data = {
            "key_name": "Test API Key",
            "expires_in_days": 90,
            "rate_limit_per_hour": 1000
        }

        response = client.post(
            "/api/v1/api-keys/",
            json=key_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert "api_key" in data  # Full key returned once
        assert "key_prefix" in data
        assert data["key_name"] == "Test API Key"
        assert data["api_key"].startswith("gp_")  # Our key prefix

    def test_generate_api_key_missing_fields(self, client, auth_headers):
        """Test API key generation with missing required fields"""
        key_data = {}

        response = client.post(
            "/api/v1/api-keys/",
            json=key_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_generate_api_key_invalid_expiry(self, client, auth_headers):
        """Test API key generation with invalid expiry"""
        key_data = {
            "key_name": "Test Key",
            "expires_in_days": 400,  # > 365 max
            "rate_limit_per_hour": 1000
        }

        response = client.post(
            "/api/v1/api-keys/",
            json=key_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_api_key_hashed_in_database(self, client, auth_headers, db):
        """Test that API key is hashed in database"""
        key_data = {
            "key_name": "Test Key",
            "expires_in_days": 90,
            "rate_limit_per_hour": 1000
        }

        response = client.post(
            "/api/v1/api-keys/",
            json=key_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        full_key = data["api_key"]

        # Verify key is hashed in database
        api_key_record = db.query(APIKey).filter(
            APIKey.key_prefix == data["key_prefix"]
        ).first()

        assert api_key_record is not None
        assert api_key_record.key_hash != full_key  # Should be hashed
        # Verify hash matches
        expected_hash = hashlib.sha256(full_key.encode()).hexdigest()
        assert api_key_record.key_hash == expected_hash


@pytest.mark.integration
class TestAPIKeyRetrieval:
    """Test API key retrieval endpoints"""

    def test_list_api_keys(self, client, auth_headers, db, test_user):
        """Test listing API keys"""
        # Create an API key
        api_key = APIKey(
            user_id=test_user.user_id,
            key_name="Test Key",
            key_prefix="gp_abc",
            key_hash=hashlib.sha256(b"test_key").hexdigest(),
            active=True,
            rate_limit_per_hour=1000,
            usage_count=0
        )
        db.add(api_key)
        db.commit()

        response = client.get("/api/v1/api-keys/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "key_hash" not in data[0]  # Hash should not be returned

    def test_get_api_key_by_id(self, client, auth_headers, db, test_user):
        """Test getting API key by ID"""
        api_key = APIKey(
            user_id=test_user.user_id,
            key_name="Test Key",
            key_prefix="gp_abc",
            key_hash=hashlib.sha256(b"test_key").hexdigest(),
            active=True,
            rate_limit_per_hour=1000,
            usage_count=0
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        response = client.get(
            f"/api/v1/api-keys/{api_key.key_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["key_id"] == api_key.key_id
        assert "key_hash" not in data  # Hash should never be returned


@pytest.mark.integration
class TestAPIKeyManagement:
    """Test API key deactivation and deletion"""

    def test_deactivate_api_key(self, client, auth_headers, db, test_user):
        """Test API key deactivation"""
        api_key = APIKey(
            user_id=test_user.user_id,
            key_name="Test Key",
            key_prefix="gp_abc",
            key_hash=hashlib.sha256(b"test_key").hexdigest(),
            active=True,
            rate_limit_per_hour=1000,
            usage_count=0
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        response = client.patch(
            f"/api/v1/api-keys/{api_key.key_id}/deactivate",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["active"] is False

    def test_activate_api_key(self, client, auth_headers, db, test_user):
        """Test API key activation"""
        api_key = APIKey(
            user_id=test_user.user_id,
            key_name="Test Key",
            key_prefix="gp_abc",
            key_hash=hashlib.sha256(b"test_key").hexdigest(),
            active=False,
            rate_limit_per_hour=1000,
            usage_count=0
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        response = client.patch(
            f"/api/v1/api-keys/{api_key.key_id}/activate",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True

    def test_delete_api_key(self, client, auth_headers, db, test_user):
        """Test API key deletion"""
        api_key = APIKey(
            user_id=test_user.user_id,
            key_name="Test Key",
            key_prefix="gp_abc",
            key_hash=hashlib.sha256(b"test_key").hexdigest(),
            active=True,
            rate_limit_per_hour=1000,
            usage_count=0
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        response = client.delete(
            f"/api/v1/api-keys/{api_key.key_id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify key is deleted
        get_response = client.get(
            f"/api/v1/api-keys/{api_key.key_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


@pytest.mark.unit
class TestAPIKeyFormat:
    """Test API key format generation"""

    def test_api_key_format(self):
        """Test API key format matches specification"""
        from app.api.api_keys import generate_api_key

        full_key, key_prefix, key_hash = generate_api_key()

        assert full_key.startswith("gp_")
        assert len(full_key) > 10  # Should be reasonably long
        assert key_prefix == full_key[:10]  # Prefix is first 10 chars
        assert len(key_hash) == 64  # SHA256 hash is 64 hex chars

    def test_api_key_uniqueness(self):
        """Test that generated API keys are unique"""
        from app.api.api_keys import generate_api_key

        key1, _, _ = generate_api_key()
        key2, _, _ = generate_api_key()

        assert key1 != key2
