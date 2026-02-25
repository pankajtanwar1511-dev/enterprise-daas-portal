"""
External System Integration Services
Slack, ServiceNow, Jira, Teams integrations
"""
import httpx
import os
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models_integrations import IntegrationLog


class SlackIntegration:
    """Slack integration service"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack integration.

        Args:
            webhook_url: Slack incoming webhook URL
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    async def send_message(
        self,
        db: Session,
        channel: str,
        message: str,
        blocks: Optional[list] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send message to Slack channel.

        Args:
            db: Database session
            channel: Slack channel name or ID
            message: Message text
            blocks: Optional Slack blocks for rich formatting
            user_id: Optional user ID triggering the message

        Returns:
            Response data with success status
        """
        if not self.webhook_url:
            return {"success": False, "message": "Slack webhook URL not configured"}

        payload = {
            "channel": channel,
            "text": message
        }

        if blocks:
            payload["blocks"] = blocks

        start_time = datetime.utcnow()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )

                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                success = response.status_code == 200

                # Log integration
                log = IntegrationLog(
                    integration_type="slack",
                    operation="send_message",
                    user_id=user_id,
                    request_payload=payload,
                    response_data={"status_code": response.status_code, "response": response.text[:500]},
                    status="success" if success else "failed",
                    duration_ms=duration_ms
                )
                db.add(log)
                db.commit()

                return {
                    "success": success,
                    "status_code": response.status_code,
                    "message": "Message sent to Slack successfully" if success else "Failed to send Slack message"
                }

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log failed integration
            log = IntegrationLog(
                integration_type="slack",
                operation="send_message",
                user_id=user_id,
                request_payload=payload,
                status="failed",
                error_message=str(e),
                duration_ms=duration_ms
            )
            db.add(log)
            db.commit()

            return {
                "success": False,
                "message": f"Slack integration error: {str(e)}"
            }

    async def notify_asset_created(self, db: Session, asset_data: Dict[str, Any]):
        """Send Slack notification when asset is created"""
        message = f"🆕 New asset created: *{asset_data.get('asset_name')}*"
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🆕 *New Asset Created*\n\n*Name:* {asset_data.get('asset_name')}\n*Environment:* {asset_data.get('environment')}\n*Domain:* {asset_data.get('domain')}"
                }
            }
        ]

        return await self.send_message(
            db,
            channel="#governance-alerts",
            message=message,
            blocks=blocks
        )

    async def notify_compliance_violation(self, db: Session, violation_data: Dict[str, Any]):
        """Send Slack notification for compliance violation"""
        message = f"⚠️ Compliance violation: {violation_data.get('description')}"
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Compliance Violation*\n\n*Asset:* {violation_data.get('asset_name')}\n*Severity:* {violation_data.get('severity')}\n*Description:* {violation_data.get('description')}"
                }
            }
        ]

        return await self.send_message(
            db,
            channel="#compliance-alerts",
            message=message,
            blocks=blocks
        )


class ServiceNowIntegration:
    """ServiceNow integration service"""

    def __init__(self, instance_url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize ServiceNow integration.

        Args:
            instance_url: ServiceNow instance URL (e.g., https://dev12345.service-now.com)
            username: ServiceNow username
            password: ServiceNow password
        """
        self.instance_url = instance_url or os.getenv("SERVICENOW_INSTANCE_URL")
        self.username = username or os.getenv("SERVICENOW_USERNAME")
        self.password = password or os.getenv("SERVICENOW_PASSWORD")
        self.auth = (self.username, self.password) if self.username and self.password else None

    async def sync_asset_to_cmdb(
        self,
        db: Session,
        asset_data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync asset to ServiceNow CMDB (Configuration Management Database).

        Args:
            db: Database session
            asset_data: Asset data to sync
            user_id: Optional user ID

        Returns:
            Response with sys_id and sync status
        """
        if not self.instance_url or not self.auth:
            return {"success": False, "message": "ServiceNow not configured"}

        # Prepare CMDB payload
        cmdb_payload = {
            "name": asset_data.get("asset_name"),
            "short_description": asset_data.get("description"),
            "u_environment": asset_data.get("environment"),
            "u_version": asset_data.get("version"),
            "u_lifecycle_stage": asset_data.get("lifecycle_stage"),
            "u_domain": asset_data.get("domain"),
            "operational_status": "1" if asset_data.get("lifecycle_stage") == "Active" else "2"
        }

        start_time = datetime.utcnow()
        endpoint = f"{self.instance_url}/api/now/table/cmdb_ci_database"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    json=cmdb_payload,
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )

                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                success = response.status_code == 201

                result_data = response.json() if success else {}
                sys_id = result_data.get("result", {}).get("sys_id")

                # Log integration
                log = IntegrationLog(
                    integration_type="servicenow",
                    operation="sync_asset_to_cmdb",
                    asset_id=asset_data.get("asset_id"),
                    user_id=user_id,
                    request_payload=cmdb_payload,
                    response_data=result_data,
                    status="success" if success else "failed",
                    duration_ms=duration_ms,
                    external_id=sys_id,
                    external_url=f"{self.instance_url}/nav_to.do?uri=cmdb_ci_database.do?sys_id={sys_id}" if sys_id else None
                )
                db.add(log)
                db.commit()

                return {
                    "success": success,
                    "sys_id": sys_id,
                    "url": log.external_url,
                    "message": "Asset synced to ServiceNow CMDB" if success else "Failed to sync asset"
                }

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log failed integration
            log = IntegrationLog(
                integration_type="servicenow",
                operation="sync_asset_to_cmdb",
                asset_id=asset_data.get("asset_id"),
                user_id=user_id,
                request_payload=cmdb_payload,
                status="failed",
                error_message=str(e),
                duration_ms=duration_ms
            )
            db.add(log)
            db.commit()

            return {
                "success": False,
                "message": f"ServiceNow integration error: {str(e)}"
            }

    async def create_incident(
        self,
        db: Session,
        short_description: str,
        description: str,
        urgency: int = 3,
        asset_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create incident ticket in ServiceNow.

        Args:
            db: Database session
            short_description: Brief description
            description: Full description
            urgency: 1=High, 2=Medium, 3=Low
            asset_id: Related asset ID
            user_id: User creating the incident

        Returns:
            Response with incident number and sys_id
        """
        if not self.instance_url or not self.auth:
            return {"success": False, "message": "ServiceNow not configured"}

        payload = {
            "short_description": short_description,
            "description": description,
            "urgency": str(urgency),
            "category": "Data Governance",
            "subcategory": "Compliance"
        }

        start_time = datetime.utcnow()
        endpoint = f"{self.instance_url}/api/now/table/incident"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )

                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                success = response.status_code == 201

                result_data = response.json() if success else {}
                sys_id = result_data.get("result", {}).get("sys_id")
                number = result_data.get("result", {}).get("number")

                # Log integration
                log = IntegrationLog(
                    integration_type="servicenow",
                    operation="create_incident",
                    asset_id=asset_id,
                    user_id=user_id,
                    request_payload=payload,
                    response_data=result_data,
                    status="success" if success else "failed",
                    duration_ms=duration_ms,
                    external_id=number,
                    external_url=f"{self.instance_url}/nav_to.do?uri=incident.do?sys_id={sys_id}" if sys_id else None
                )
                db.add(log)
                db.commit()

                return {
                    "success": success,
                    "sys_id": sys_id,
                    "number": number,
                    "url": log.external_url,
                    "message": f"Incident {number} created" if success else "Failed to create incident"
                }

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log failed integration
            log = IntegrationLog(
                integration_type="servicenow",
                operation="create_incident",
                asset_id=asset_id,
                user_id=user_id,
                request_payload=payload,
                status="failed",
                error_message=str(e),
                duration_ms=duration_ms
            )
            db.add(log)
            db.commit()

            return {
                "success": False,
                "message": f"ServiceNow integration error: {str(e)}"
            }
