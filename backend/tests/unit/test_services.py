"""
Unit tests for service layer (webhook service, integration services)
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.webhook_service import WebhookService
from app.services.integrations import SlackIntegration, ServiceNowIntegration
from app.models_integrations import Webhook, WebhookDelivery
import httpx


@pytest.mark.unit
class TestWebhookService:
    """Test webhook service functionality"""

    @pytest.mark.asyncio
    async def test_trigger_event_no_webhooks(self, db):
        """Test triggering event when no webhooks exist"""
        result = await WebhookService.trigger_event(
            db=db,
            event_type="asset.created",
            payload={"asset_id": 1}
        )

        assert result["total_webhooks"] == 0
        assert result["successful"] == 0
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_trigger_event_with_inactive_webhook(self, db, test_user):
        """Test that inactive webhooks are not triggered"""
        # Create inactive webhook
        webhook = Webhook(
            name="Inactive Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.created"],
            active=False,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()

        result = await WebhookService.trigger_event(
            db=db,
            event_type="asset.created",
            payload={"asset_id": 1}
        )

        assert result["total_webhooks"] == 0  # Inactive not counted

    @pytest.mark.asyncio
    async def test_trigger_event_unsubscribed_event(self, db, test_user):
        """Test that webhooks not subscribed to event are not triggered"""
        # Create webhook subscribed to different event
        webhook = Webhook(
            name="Test Webhook",
            url="https://webhook.site/test",
            secret="test_secret",
            events=["asset.deleted"],  # Different event
            active=True,
            created_by=test_user.user_id,
            retry_count=3,
            timeout_seconds=10
        )
        db.add(webhook)
        db.commit()

        result = await WebhookService.trigger_event(
            db=db,
            event_type="asset.created",  # Different from subscription
            payload={"asset_id": 1}
        )

        assert result["total_webhooks"] == 0  # Not subscribed


@pytest.mark.unit
class TestSlackIntegration:
    """Test Slack integration service"""

    def test_slack_integration_initialization(self):
        """Test Slack integration initialization"""
        slack = SlackIntegration()
        assert slack.webhook_url is None or isinstance(slack.webhook_url, str)

    def test_slack_integration_with_custom_url(self):
        """Test Slack integration with custom webhook URL"""
        test_url = "https://hooks.slack.com/services/TEST/WEBHOOK/URL"
        slack = SlackIntegration(webhook_url=test_url)
        assert slack.webhook_url == test_url

    @pytest.mark.asyncio
    async def test_send_message_no_webhook_url(self, db):
        """Test sending message without webhook URL configured"""
        slack = SlackIntegration(webhook_url=None)

        result = await slack.send_message(
            db=db,
            channel="#test",
            message="Test message"
        )

        assert result["success"] is False
        assert "not configured" in result["message"].lower()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_message_success(self, mock_client, db):
        """Test successful Slack message sending"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "ok"

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")

        result = await slack.send_message(
            db=db,
            channel="#test",
            message="Test message"
        )

        assert result["success"] is True
        assert "successfully" in result["message"].lower()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_message_failure(self, mock_client, db):
        """Test failed Slack message sending"""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")

        result = await slack.send_message(
            db=db,
            channel="#test",
            message="Test message"
        )

        assert result["success"] is False

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_message_with_blocks(self, mock_client, db):
        """Test sending Slack message with rich formatting blocks"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "ok"

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Bold text*"
                }
            }
        ]

        result = await slack.send_message(
            db=db,
            channel="#test",
            message="Test message",
            blocks=blocks
        )

        assert result["success"] is True
        # Verify blocks were included in payload
        call_args = mock_post.call_args
        assert "blocks" in call_args[1]["json"]

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_notify_asset_created(self, mock_client, db):
        """Test asset creation notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "ok"

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        slack = SlackIntegration(webhook_url="https://hooks.slack.com/test")

        asset_data = {
            "asset_name": "PROD-HR-DW-v1",
            "environment": "PROD",
            "domain": "HR"
        }

        result = await slack.notify_asset_created(db, asset_data)

        assert result["success"] is True
        # Verify message content
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "PROD-HR-DW-v1" in payload["message"]


@pytest.mark.unit
class TestServiceNowIntegration:
    """Test ServiceNow integration service"""

    def test_servicenow_initialization(self):
        """Test ServiceNow integration initialization"""
        snow = ServiceNowIntegration()
        assert snow.instance_url is None or isinstance(snow.instance_url, str)

    def test_servicenow_with_custom_config(self):
        """Test ServiceNow with custom configuration"""
        snow = ServiceNowIntegration(
            instance_url="https://dev12345.service-now.com",
            username="test_user",
            password="test_password"
        )

        assert snow.instance_url == "https://dev12345.service-now.com"
        assert snow.username == "test_user"
        assert snow.auth == ("test_user", "test_password")

    @pytest.mark.asyncio
    async def test_sync_asset_no_config(self, db):
        """Test syncing asset without ServiceNow configured"""
        snow = ServiceNowIntegration(instance_url=None)

        result = await snow.sync_asset_to_cmdb(db, {})

        assert result["success"] is False
        assert "not configured" in result["message"].lower()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_sync_asset_to_cmdb_success(self, mock_client, db):
        """Test successful asset sync to ServiceNow CMDB"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "result": {"sys_id": "abc123"}
        }

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        snow = ServiceNowIntegration(
            instance_url="https://dev12345.service-now.com",
            username="test",
            password="test"
        )

        asset_data = {
            "asset_id": 1,
            "asset_name": "PROD-HR-DW-v1",
            "description": "HR Data Warehouse",
            "environment": "PROD",
            "version": "v1.0",
            "lifecycle_stage": "Active",
            "domain": "HR"
        }

        result = await snow.sync_asset_to_cmdb(db, asset_data)

        assert result["success"] is True
        assert result["sys_id"] == "abc123"
        assert "service-now.com" in result["url"]

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_incident_success(self, mock_client, db):
        """Test successful incident creation in ServiceNow"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "result": {
                "sys_id": "inc123",
                "number": "INC0012345"
            }
        }

        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post

        snow = ServiceNowIntegration(
            instance_url="https://dev12345.service-now.com",
            username="test",
            password="test"
        )

        result = await snow.create_incident(
            db=db,
            short_description="Test incident",
            description="Full description",
            urgency=1
        )

        assert result["success"] is True
        assert result["number"] == "INC0012345"
        assert result["sys_id"] == "inc123"

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_sync_asset_exception_handling(self, mock_client, db):
        """Test exception handling in asset sync"""
        # Mock exception
        mock_post = AsyncMock(side_effect=Exception("Network error"))
        mock_client.return_value.__aenter__.return_value.post = mock_post

        snow = ServiceNowIntegration(
            instance_url="https://dev12345.service-now.com",
            username="test",
            password="test"
        )

        result = await snow.sync_asset_to_cmdb(db, {"asset_id": 1})

        assert result["success"] is False
        assert "error" in result["message"].lower()
