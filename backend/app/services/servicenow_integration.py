"""
ServiceNow Integration Service

Handles bidirectional sync between the Portal and ServiceNow.
Supports change requests, incidents, and configuration items.
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models_itsm import (
    ITSMConfiguration, ITSMRecordMapping, ITSMSyncLog,
    ITSMSystem, SyncDirection, SyncStatus, ServiceNowRecordType
)
from ..models import ChangeRequest
from ..logging_config import get_logger

logger = get_logger(__name__)


class ServiceNowClient:
    """
    ServiceNow REST API client

    Handles authentication and API calls to ServiceNow.
    """

    def __init__(self, config: ITSMConfiguration):
        """
        Initialize ServiceNow client

        Args:
            config: ITSM configuration with ServiceNow details
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.username = config.username
        # In production, decrypt the password
        self.password = config.password_encrypted  # TODO: Implement decryption
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to ServiceNow

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/api/now/table/change_request')
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        logger.debug(
            "servicenow_request",
            method=method,
            url=url,
            has_data=data is not None
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            result = response.json() if response.text else {}

            logger.debug(
                "servicenow_response",
                status_code=response.status_code,
                has_result=bool(result)
            )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(
                "servicenow_request_failed",
                method=method,
                url=url,
                error=str(e)
            )
            raise

    def create_change_request(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a change request in ServiceNow"""
        endpoint = "/api/now/table/change_request"
        return self._make_request("POST", endpoint, data=change_data)

    def update_change_request(self, sys_id: str, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a change request in ServiceNow"""
        endpoint = f"/api/now/table/change_request/{sys_id}"
        return self._make_request("PATCH", endpoint, data=change_data)

    def get_change_request(self, sys_id: str) -> Dict[str, Any]:
        """Get a change request from ServiceNow"""
        endpoint = f"/api/now/table/change_request/{sys_id}"
        return self._make_request("GET", endpoint)

    def query_change_requests(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query change requests from ServiceNow"""
        endpoint = "/api/now/table/change_request"
        params = {
            "sysparm_query": query,
            "sysparm_limit": limit
        }
        result = self._make_request("GET", endpoint, params=params)
        return result.get("result", [])

    def create_configuration_item(self, ci_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a configuration item in ServiceNow"""
        endpoint = "/api/now/table/cmdb_ci"
        return self._make_request("POST", endpoint, data=ci_data)

    def update_configuration_item(self, sys_id: str, ci_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a configuration item in ServiceNow"""
        endpoint = f"/api/now/table/cmdb_ci/{sys_id}"
        return self._make_request("PATCH", endpoint, data=ci_data)


class ServiceNowIntegration:
    """
    ServiceNow Integration Service

    Handles bidirectional sync of change requests and assets.
    """

    def __init__(self, db: Session, config: ITSMConfiguration):
        """
        Initialize ServiceNow integration

        Args:
            db: Database session
            config: ITSM configuration
        """
        self.db = db
        self.config = config
        self.client = ServiceNowClient(config)

    def sync_change_request_to_servicenow(
        self,
        change_request: ChangeRequest
    ) -> ITSMRecordMapping:
        """
        Sync a Portal change request to ServiceNow

        Args:
            change_request: Portal change request to sync

        Returns:
            ITSM record mapping

        Raises:
            Exception: If sync fails
        """
        start_time = datetime.utcnow()

        try:
            # Check if mapping already exists
            mapping = self.db.query(ITSMRecordMapping).filter(
                ITSMRecordMapping.config_id == self.config.config_id,
                ITSMRecordMapping.entity_type == "change_request",
                ITSMRecordMapping.entity_id == change_request.request_id
            ).first()

            # Map Portal fields to ServiceNow fields
            servicenow_data = self._map_change_request_to_servicenow(change_request)

            if mapping:
                # Update existing ServiceNow change request
                response = self.client.update_change_request(
                    mapping.itsm_record_id,
                    servicenow_data
                )
                operation = "update"
            else:
                # Create new ServiceNow change request
                response = self.client.create_change_request(servicenow_data)
                operation = "create"

                # Create mapping
                mapping = ITSMRecordMapping(
                    config_id=self.config.config_id,
                    entity_type="change_request",
                    entity_id=change_request.request_id,
                    itsm_record_type=ServiceNowRecordType.CHANGE_REQUEST.value,
                    itsm_record_id=response["result"]["sys_id"],
                    itsm_record_number=response["result"].get("number"),
                    itsm_record_url=f"{self.config.base_url}/change_request.do?sys_id={response['result']['sys_id']}",
                    sync_direction=SyncDirection.TO_ITSM,
                    last_sync_status=SyncStatus.COMPLETED
                )
                self.db.add(mapping)

            # Update mapping
            mapping.last_synced_at = datetime.utcnow()
            mapping.last_sync_status = SyncStatus.COMPLETED
            mapping.portal_version += 1

            # Create sync log
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_log = ITSMSyncLog(
                config_id=self.config.config_id,
                mapping_id=mapping.mapping_id if mapping.mapping_id else None,
                sync_direction=SyncDirection.TO_ITSM,
                operation=operation,
                status=SyncStatus.COMPLETED,
                entity_type="change_request",
                entity_id=change_request.request_id,
                itsm_record_type=ServiceNowRecordType.CHANGE_REQUEST.value,
                itsm_record_id=response["result"]["sys_id"],
                success=True,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms
            )
            self.db.add(sync_log)

            self.db.commit()
            self.db.refresh(mapping)

            logger.info(
                "change_request_synced_to_servicenow",
                request_id=change_request.request_id,
                servicenow_id=mapping.itsm_record_id,
                operation=operation
            )

            return mapping

        except Exception as e:
            self.db.rollback()

            # Create failure log
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_log = ITSMSyncLog(
                config_id=self.config.config_id,
                sync_direction=SyncDirection.TO_ITSM,
                operation="create" if not mapping else "update",
                status=SyncStatus.FAILED,
                entity_type="change_request",
                entity_id=change_request.request_id,
                itsm_record_type=ServiceNowRecordType.CHANGE_REQUEST.value,
                success=False,
                error_message=str(e),
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms
            )
            self.db.add(sync_log)
            self.db.commit()

            logger.error(
                "change_request_sync_failed",
                request_id=change_request.request_id,
                error=str(e)
            )

            raise

    def sync_change_request_from_servicenow(
        self,
        servicenow_sys_id: str
    ) -> ChangeRequest:
        """
        Sync a ServiceNow change request to the Portal

        Args:
            servicenow_sys_id: ServiceNow sys_id

        Returns:
            Portal change request

        Raises:
            Exception: If sync fails
        """
        start_time = datetime.utcnow()

        try:
            # Fetch from ServiceNow
            response = self.client.get_change_request(servicenow_sys_id)
            servicenow_cr = response["result"]

            # Check if mapping exists
            mapping = self.db.query(ITSMRecordMapping).filter(
                ITSMRecordMapping.config_id == self.config.config_id,
                ITSMRecordMapping.itsm_record_id == servicenow_sys_id
            ).first()

            # Map ServiceNow fields to Portal fields
            portal_data = self._map_servicenow_to_change_request(servicenow_cr)

            if mapping:
                # Update existing Portal change request
                change_request = self.db.query(ChangeRequest).get(mapping.entity_id)
                for key, value in portal_data.items():
                    setattr(change_request, key, value)
                operation = "update"
            else:
                # Create new Portal change request
                change_request = ChangeRequest(**portal_data)
                self.db.add(change_request)
                self.db.flush()  # Get change_request.request_id
                operation = "create"

                # Create mapping
                mapping = ITSMRecordMapping(
                    config_id=self.config.config_id,
                    entity_type="change_request",
                    entity_id=change_request.request_id,
                    itsm_record_type=ServiceNowRecordType.CHANGE_REQUEST.value,
                    itsm_record_id=servicenow_sys_id,
                    itsm_record_number=servicenow_cr.get("number"),
                    itsm_record_url=f"{self.config.base_url}/change_request.do?sys_id={servicenow_sys_id}",
                    sync_direction=SyncDirection.FROM_ITSM,
                    last_sync_status=SyncStatus.COMPLETED
                )
                self.db.add(mapping)

            # Update mapping
            mapping.last_synced_at = datetime.utcnow()
            mapping.last_sync_status = SyncStatus.COMPLETED

            # Create sync log
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_log = ITSMSyncLog(
                config_id=self.config.config_id,
                mapping_id=mapping.mapping_id,
                sync_direction=SyncDirection.FROM_ITSM,
                operation=operation,
                status=SyncStatus.COMPLETED,
                entity_type="change_request",
                entity_id=change_request.request_id,
                itsm_record_type=ServiceNowRecordType.CHANGE_REQUEST.value,
                itsm_record_id=servicenow_sys_id,
                success=True,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms
            )
            self.db.add(sync_log)

            self.db.commit()
            self.db.refresh(change_request)

            logger.info(
                "change_request_synced_from_servicenow",
                servicenow_id=servicenow_sys_id,
                request_id=change_request.request_id,
                operation=operation
            )

            return change_request

        except Exception as e:
            self.db.rollback()

            logger.error(
                "servicenow_sync_failed",
                servicenow_id=servicenow_sys_id,
                error=str(e)
            )

            raise

    def _map_change_request_to_servicenow(
        self,
        change_request: ChangeRequest
    ) -> Dict[str, Any]:
        """Map Portal change request to ServiceNow format"""
        # Use field mappings from configuration if available
        field_mappings = self.config.field_mappings or {}

        # Default mapping
        servicenow_data = {
            "short_description": change_request.change_title,
            "description": change_request.description or "",
            "justification": change_request.business_justification or "",
            "implementation_plan": change_request.implementation_plan or "",
            "rollback_plan": change_request.rollback_plan or "",
            "priority": self._map_priority(change_request.priority),
            "risk": self._map_risk(change_request.risk_level),
            "start_date": change_request.planned_start_date.isoformat() if change_request.planned_start_date else None,
            "end_date": change_request.planned_end_date.isoformat() if change_request.planned_end_date else None,
        }

        # Apply custom field mappings
        for portal_field, snow_field in field_mappings.items():
            if hasattr(change_request, portal_field):
                servicenow_data[snow_field] = getattr(change_request, portal_field)

        return servicenow_data

    def _map_servicenow_to_change_request(
        self,
        servicenow_cr: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map ServiceNow change request to Portal format"""
        return {
            "change_title": servicenow_cr.get("short_description", ""),
            "description": servicenow_cr.get("description", ""),
            "business_justification": servicenow_cr.get("justification", ""),
            "implementation_plan": servicenow_cr.get("implementation_plan", ""),
            "rollback_plan": servicenow_cr.get("rollback_plan", ""),
            # Map other fields as needed
        }

    def _map_priority(self, priority: str) -> str:
        """Map Portal priority to ServiceNow priority"""
        priority_map = {
            "Critical": "1",
            "High": "2",
            "Medium": "3",
            "Low": "4"
        }
        return priority_map.get(priority, "3")

    def _map_risk(self, risk: str) -> str:
        """Map Portal risk to ServiceNow risk"""
        risk_map = {
            "High": "high",
            "Medium": "medium",
            "Low": "low"
        }
        return risk_map.get(risk, "medium")
