"""
ITSM Integration Models

Models for integrating with ITSM systems (ServiceNow, Jira).
Supports bidirectional sync, mapping, and status tracking.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


# ==================== Enums ====================

class ITSMSystem(str, enum.Enum):
    """Supported ITSM systems"""
    SERVICENOW = "ServiceNow"
    JIRA = "Jira"


class SyncDirection(str, enum.Enum):
    """Sync direction"""
    TO_ITSM = "to_itsm"          # Push from Portal to ITSM
    FROM_ITSM = "from_itsm"      # Pull from ITSM to Portal
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, enum.Enum):
    """Sync status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"        # Bidirectional conflict detected


class ServiceNowRecordType(str, enum.Enum):
    """ServiceNow record types we sync"""
    INCIDENT = "incident"
    CHANGE_REQUEST = "change_request"
    SERVICE_REQUEST = "service_request"
    PROBLEM = "problem"
    CONFIGURATION_ITEM = "configuration_item"


class JiraIssueType(str, enum.Enum):
    """Jira issue types"""
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    SUBTASK = "subtask"


# ==================== Models ====================

class ITSMConfiguration(Base):
    """
    ITSM System Configuration

    Stores connection details and settings for ITSM integrations.
    Supports multiple instances of the same ITSM system.
    """
    __tablename__ = "itsm_configurations"

    config_id = Column(Integer, primary_key=True, index=True)
    system_type = Column(Enum(ITSMSystem), nullable=False)
    instance_name = Column(String(100), nullable=False)  # e.g., "Production ServiceNow"

    # Connection details
    base_url = Column(String(255), nullable=False)
    api_endpoint = Column(String(255), nullable=True)
    username = Column(String(100), nullable=True)
    password_encrypted = Column(Text, nullable=True)  # Encrypted password
    api_token_encrypted = Column(Text, nullable=True)  # Encrypted API token
    oauth_config = Column(JSON, nullable=True)  # OAuth configuration

    # Sync settings
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL, nullable=False)
    sync_interval_minutes = Column(Integer, default=15, nullable=False)  # How often to sync
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)

    # Field mappings (JSON)
    field_mappings = Column(JSON, nullable=True)  # Maps Portal fields to ITSM fields

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Status
    active = Column(Boolean, default=True, nullable=False)
    last_error = Column(Text, nullable=True)

    # Relationships
    creator = relationship("User", backref="itsm_configs")
    record_mappings = relationship("ITSMRecordMapping", back_populates="config", cascade="all, delete-orphan")
    sync_logs = relationship("ITSMSyncLog", back_populates="config", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary (exclude sensitive data)"""
        return {
            "config_id": self.config_id,
            "system_type": self.system_type.value if self.system_type else None,
            "instance_name": self.instance_name,
            "base_url": self.base_url,
            "sync_enabled": self.sync_enabled,
            "sync_direction": self.sync_direction.value if self.sync_direction else None,
            "sync_interval_minutes": self.sync_interval_minutes,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "next_sync_at": self.next_sync_at.isoformat() if self.next_sync_at else None,
            "active": self.active,
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ITSMRecordMapping(Base):
    """
    ITSM Record Mapping

    Maps Portal records (assets, change requests, etc.) to ITSM records.
    Enables bidirectional sync and conflict resolution.
    """
    __tablename__ = "itsm_record_mappings"

    mapping_id = Column(Integer, primary_key=True, index=True)

    # ITSM configuration
    config_id = Column(Integer, ForeignKey("itsm_configurations.config_id"), nullable=False, index=True)

    # Portal entity
    entity_type = Column(String(50), nullable=False, index=True)  # 'asset', 'change_request', etc.
    entity_id = Column(Integer, nullable=False, index=True)

    # ITSM record
    itsm_record_type = Column(String(50), nullable=False)  # ServiceNow: 'incident', Jira: 'epic'
    itsm_record_id = Column(String(100), nullable=False, index=True)  # External system ID
    itsm_record_number = Column(String(50), nullable=True)  # Human-readable number (e.g., INC0010001)
    itsm_record_url = Column(String(500), nullable=True)  # Direct link to ITSM record

    # Sync tracking
    sync_direction = Column(Enum(SyncDirection), nullable=False)
    last_synced_at = Column(DateTime, nullable=True)
    last_sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    last_sync_error = Column(Text, nullable=True)

    # Version tracking (for conflict detection)
    portal_version = Column(Integer, default=1, nullable=False)  # Incremented on each update
    itsm_version = Column(String(50), nullable=True)  # ITSM system's version/timestamp

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    config = relationship("ITSMConfiguration", back_populates="record_mappings")
    sync_logs = relationship("ITSMSyncLog", back_populates="mapping", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "mapping_id": self.mapping_id,
            "config_id": self.config_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "itsm_record_type": self.itsm_record_type,
            "itsm_record_id": self.itsm_record_id,
            "itsm_record_number": self.itsm_record_number,
            "itsm_record_url": self.itsm_record_url,
            "sync_direction": self.sync_direction.value if self.sync_direction else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "last_sync_status": self.last_sync_status.value if self.last_sync_status else None,
            "last_sync_error": self.last_sync_error,
            "active": self.active,
        }


class ITSMSyncLog(Base):
    """
    ITSM Sync Log

    Comprehensive audit log of all sync operations.
    Tracks what changed, when, and any errors.
    """
    __tablename__ = "itsm_sync_logs"

    log_id = Column(Integer, primary_key=True, index=True)

    # Configuration and mapping
    config_id = Column(Integer, ForeignKey("itsm_configurations.config_id"), nullable=False, index=True)
    mapping_id = Column(Integer, ForeignKey("itsm_record_mappings.mapping_id"), nullable=True, index=True)

    # Sync operation details
    sync_direction = Column(Enum(SyncDirection), nullable=False)
    operation = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    status = Column(Enum(SyncStatus), nullable=False)

    # What was synced
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    itsm_record_type = Column(String(50), nullable=False)
    itsm_record_id = Column(String(100), nullable=True)

    # Change details
    fields_changed = Column(JSON, nullable=True)  # List of field names that changed
    before_values = Column(JSON, nullable=True)  # Values before sync
    after_values = Column(JSON, nullable=True)  # Values after sync

    # Result
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)  # Detailed error information

    # Timing
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)  # Duration in milliseconds

    # HTTP details (for debugging)
    http_method = Column(String(10), nullable=True)  # GET, POST, PUT, PATCH
    http_status_code = Column(Integer, nullable=True)
    http_response_body = Column(Text, nullable=True)

    # Relationships
    config = relationship("ITSMConfiguration", back_populates="sync_logs")
    mapping = relationship("ITSMRecordMapping", back_populates="sync_logs")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "log_id": self.log_id,
            "config_id": self.config_id,
            "mapping_id": self.mapping_id,
            "sync_direction": self.sync_direction.value if self.sync_direction else None,
            "operation": self.operation,
            "status": self.status.value if self.status else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "itsm_record_type": self.itsm_record_type,
            "itsm_record_id": self.itsm_record_id,
            "success": self.success,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }
