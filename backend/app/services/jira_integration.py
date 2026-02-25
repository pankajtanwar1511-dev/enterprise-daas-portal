"""
Jira Integration Service

Handles integration with Jira for strategic initiative tracking.
Supports creating epics and stories from Portal initiatives.
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..models_itsm import (
    ITSMConfiguration, ITSMRecordMapping, ITSMSyncLog,
    ITSMSystem, SyncDirection, SyncStatus, JiraIssueType
)
from ..models_extended import StrategicInitiative, InitiativeDeliverable
from ..logging_config import get_logger

logger = get_logger(__name__)


class JiraClient:
    """
    Jira REST API client

    Handles authentication and API calls to Jira.
    """

    def __init__(self, config: ITSMConfiguration):
        """
        Initialize Jira client

        Args:
            config: ITSM configuration with Jira details
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.api_url = f"{self.base_url}/rest/api/3"

        # Support both basic auth and API token
        if config.api_token_encrypted:
            # API token auth (recommended)
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {config.api_token_encrypted}",  # TODO: Decrypt
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
        else:
            # Basic auth
            self.session = requests.Session()
            self.session.auth = (config.username, config.password_encrypted)  # TODO: Decrypt
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
        Make HTTP request to Jira

        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., '/issue')
            data: Request body
            params: Query parameters

        Returns:
            Response data

        Raises:
            Exception: If request fails
        """
        url = f"{self.api_url}{endpoint}"

        logger.debug(
            "jira_request",
            method=method,
            endpoint=endpoint,
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
                "jira_response",
                status_code=response.status_code,
                has_result=bool(result)
            )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(
                "jira_request_failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )
            raise

    def create_epic(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an epic in Jira"""
        return self._make_request("POST", "/issue", data=epic_data)

    def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a story in Jira"""
        return self._make_request("POST", "/issue", data=story_data)

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task in Jira"""
        return self._make_request("POST", "/issue", data=task_data)

    def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue"""
        return self._make_request("PUT", f"/issue/{issue_key}", data=update_data)

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get a Jira issue"""
        return self._make_request("GET", f"/issue/{issue_key}")

    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for Jira issues using JQL"""
        params = {
            "jql": jql,
            "maxResults": max_results
        }
        result = self._make_request("GET", "/search", params=params)
        return result.get("issues", [])

    def link_issue_to_epic(self, issue_key: str, epic_key: str) -> None:
        """Link a story/task to an epic"""
        # In Jira Cloud, epics use a different field
        update_data = {
            "fields": {
                "parent": {
                    "key": epic_key
                }
            }
        }
        self._make_request("PUT", f"/issue/{issue_key}", data=update_data)


class JiraIntegration:
    """
    Jira Integration Service

    Handles creating and syncing strategic initiatives as epics in Jira.
    """

    def __init__(self, db: Session, config: ITSMConfiguration):
        """
        Initialize Jira integration

        Args:
            db: Database session
            config: ITSM configuration
        """
        self.db = db
        self.config = config
        self.client = JiraClient(config)

    def create_epic_from_initiative(
        self,
        initiative: StrategicInitiative,
        project_key: str
    ) -> ITSMRecordMapping:
        """
        Create a Jira epic from a strategic initiative

        Args:
            initiative: Portal strategic initiative
            project_key: Jira project key (e.g., 'DAAS')

        Returns:
            ITSM record mapping

        Raises:
            Exception: If creation fails
        """
        start_time = datetime.utcnow()

        try:
            # Check if mapping already exists
            mapping = self.db.query(ITSMRecordMapping).filter(
                ITSMRecordMapping.config_id == self.config.config_id,
                ITSMRecordMapping.entity_type == "initiative",
                ITSMRecordMapping.entity_id == initiative.initiative_id
            ).first()

            if mapping:
                logger.warning(
                    "jira_epic_already_exists",
                    initiative_id=initiative.initiative_id,
                    jira_key=mapping.itsm_record_number
                )
                return mapping

            # Build epic data
            epic_data = {
                "fields": {
                    "project": {
                        "key": project_key
                    },
                    "summary": initiative.initiative_name,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": initiative.description or ""
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {
                        "name": "Epic"
                    },
                    "labels": ["daas-portal", f"initiative-{initiative.initiative_id}"],
                }
            }

            # Add custom fields from configuration
            if self.config.field_mappings:
                for portal_field, jira_field in self.config.field_mappings.items():
                    if hasattr(initiative, portal_field):
                        epic_data["fields"][jira_field] = getattr(initiative, portal_field)

            # Create epic in Jira
            response = self.client.create_epic(epic_data)

            # Create mapping
            mapping = ITSMRecordMapping(
                config_id=self.config.config_id,
                entity_type="initiative",
                entity_id=initiative.initiative_id,
                itsm_record_type=JiraIssueType.EPIC.value,
                itsm_record_id=response["id"],
                itsm_record_number=response["key"],
                itsm_record_url=f"{self.config.base_url}/browse/{response['key']}",
                sync_direction=SyncDirection.TO_ITSM,
                last_sync_status=SyncStatus.COMPLETED,
                last_synced_at=datetime.utcnow()
            )
            self.db.add(mapping)

            # Create sync log
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_log = ITSMSyncLog(
                config_id=self.config.config_id,
                mapping_id=None,  # Will be set after commit
                sync_direction=SyncDirection.TO_ITSM,
                operation="create",
                status=SyncStatus.COMPLETED,
                entity_type="initiative",
                entity_id=initiative.initiative_id,
                itsm_record_type=JiraIssueType.EPIC.value,
                itsm_record_id=response["id"],
                success=True,
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms
            )
            self.db.add(sync_log)

            self.db.commit()
            self.db.refresh(mapping)

            logger.info(
                "jira_epic_created",
                initiative_id=initiative.initiative_id,
                jira_key=response["key"],
                jira_id=response["id"]
            )

            return mapping

        except Exception as e:
            self.db.rollback()

            # Create failure log
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            sync_log = ITSMSyncLog(
                config_id=self.config.config_id,
                sync_direction=SyncDirection.TO_ITSM,
                operation="create",
                status=SyncStatus.FAILED,
                entity_type="initiative",
                entity_id=initiative.initiative_id,
                itsm_record_type=JiraIssueType.EPIC.value,
                success=False,
                error_message=str(e),
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_ms=duration_ms
            )
            self.db.add(sync_log)
            self.db.commit()

            logger.error(
                "jira_epic_creation_failed",
                initiative_id=initiative.initiative_id,
                error=str(e)
            )

            raise

    def create_stories_from_deliverables(
        self,
        initiative: StrategicInitiative,
        project_key: str
    ) -> List[ITSMRecordMapping]:
        """
        Create Jira stories from initiative deliverables

        Args:
            initiative: Portal strategic initiative
            project_key: Jira project key

        Returns:
            List of ITSM record mappings

        Raises:
            Exception: If creation fails
        """
        # First, ensure epic exists
        epic_mapping = self.db.query(ITSMRecordMapping).filter(
            ITSMRecordMapping.config_id == self.config.config_id,
            ITSMRecordMapping.entity_type == "initiative",
            ITSMRecordMapping.entity_id == initiative.initiative_id
        ).first()

        if not epic_mapping:
            # Create epic first
            epic_mapping = self.create_epic_from_initiative(initiative, project_key)

        epic_key = epic_mapping.itsm_record_number

        # Create stories for each deliverable
        story_mappings = []

        for deliverable in initiative.deliverables:
            try:
                start_time = datetime.utcnow()

                # Check if story already exists
                existing_mapping = self.db.query(ITSMRecordMapping).filter(
                    ITSMRecordMapping.config_id == self.config.config_id,
                    ITSMRecordMapping.entity_type == "deliverable",
                    ITSMRecordMapping.entity_id == deliverable.deliverable_id
                ).first()

                if existing_mapping:
                    logger.info(
                        "jira_story_already_exists",
                        deliverable_id=deliverable.deliverable_id,
                        jira_key=existing_mapping.itsm_record_number
                    )
                    story_mappings.append(existing_mapping)
                    continue

                # Build story data
                story_data = {
                    "fields": {
                        "project": {
                            "key": project_key
                        },
                        "parent": {
                            "key": epic_key
                        },
                        "summary": deliverable.deliverable_name,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": deliverable.description or ""
                                        }
                                    ]
                                }
                            ]
                        },
                        "issuetype": {
                            "name": "Story"
                        },
                        "labels": [
                            "daas-portal",
                            f"initiative-{initiative.initiative_id}",
                            f"deliverable-{deliverable.deliverable_id}"
                        ],
                    }
                }

                # Add due date if available
                if deliverable.target_completion_date:
                    story_data["fields"]["duedate"] = deliverable.target_completion_date.isoformat()

                # Create story in Jira
                response = self.client.create_story(story_data)

                # Create mapping
                mapping = ITSMRecordMapping(
                    config_id=self.config.config_id,
                    entity_type="deliverable",
                    entity_id=deliverable.deliverable_id,
                    itsm_record_type=JiraIssueType.STORY.value,
                    itsm_record_id=response["id"],
                    itsm_record_number=response["key"],
                    itsm_record_url=f"{self.config.base_url}/browse/{response['key']}",
                    sync_direction=SyncDirection.TO_ITSM,
                    last_sync_status=SyncStatus.COMPLETED,
                    last_synced_at=datetime.utcnow()
                )
                self.db.add(mapping)

                # Create sync log
                duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                sync_log = ITSMSyncLog(
                    config_id=self.config.config_id,
                    sync_direction=SyncDirection.TO_ITSM,
                    operation="create",
                    status=SyncStatus.COMPLETED,
                    entity_type="deliverable",
                    entity_id=deliverable.deliverable_id,
                    itsm_record_type=JiraIssueType.STORY.value,
                    itsm_record_id=response["id"],
                    success=True,
                    started_at=start_time,
                    completed_at=datetime.utcnow(),
                    duration_ms=duration_ms
                )
                self.db.add(sync_log)

                self.db.commit()
                self.db.refresh(mapping)

                story_mappings.append(mapping)

                logger.info(
                    "jira_story_created",
                    deliverable_id=deliverable.deliverable_id,
                    jira_key=response["key"],
                    epic_key=epic_key
                )

            except Exception as e:
                logger.error(
                    "jira_story_creation_failed",
                    deliverable_id=deliverable.deliverable_id,
                    error=str(e)
                )
                # Continue with other deliverables

        return story_mappings

    def sync_initiative_status_to_jira(
        self,
        initiative: StrategicInitiative
    ) -> bool:
        """
        Sync initiative status to Jira epic

        Args:
            initiative: Portal strategic initiative

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get epic mapping
            mapping = self.db.query(ITSMRecordMapping).filter(
                ITSMRecordMapping.config_id == self.config.config_id,
                ITSMRecordMapping.entity_type == "initiative",
                ITSMRecordMapping.entity_id == initiative.initiative_id
            ).first()

            if not mapping:
                logger.warning(
                    "jira_epic_mapping_not_found",
                    initiative_id=initiative.initiative_id
                )
                return False

            # Map Portal status to Jira status
            status_map = {
                "Planning": "To Do",
                "In Progress": "In Progress",
                "On Hold": "On Hold",
                "Completed": "Done",
                "Cancelled": "Done"
            }

            jira_status = status_map.get(initiative.status, "To Do")

            # Update epic status in Jira
            update_data = {
                "fields": {
                    "status": {
                        "name": jira_status
                    }
                }
            }

            self.client.update_issue(mapping.itsm_record_number, update_data)

            logger.info(
                "jira_epic_status_updated",
                initiative_id=initiative.initiative_id,
                jira_key=mapping.itsm_record_number,
                new_status=jira_status
            )

            return True

        except Exception as e:
            logger.error(
                "jira_status_sync_failed",
                initiative_id=initiative.initiative_id,
                error=str(e)
            )
            return False
