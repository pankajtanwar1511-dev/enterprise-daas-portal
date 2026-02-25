"""
Integration Models for Phase 3: Enterprise Integration
Includes Webhooks, API Keys, and Integration tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class WebhookEventType(str, enum.Enum):
    """Webhook event types"""
    ASSET_CREATED = "asset.created"
    ASSET_UPDATED = "asset.updated"
    ASSET_DELETED = "asset.deleted"
    COMPLIANCE_VIOLATION = "compliance.violation"
    CHANGE_APPROVED = "change.approved"
    CHANGE_REJECTED = "change.rejected"
    SLA_BREACHED = "sla.breached"
    BUDGET_THRESHOLD = "budget.threshold"
    USER_CREATED = "user.created"


class Webhook(Base):
    """
    Webhook configuration for external system notifications
    """
    __tablename__ = "webhooks"

    webhook_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)  # For signature verification

    # Event subscriptions (stored as JSON array)
    events = Column(JSON, nullable=False)  # List of WebhookEventType values

    # Status and metadata
    active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_triggered = Column(DateTime, nullable=True)

    # Delivery settings
    retry_count = Column(Integer, default=3, nullable=False)
    timeout_seconds = Column(Integer, default=10, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Webhook {self.webhook_id}: {self.name}>"


class WebhookDelivery(Base):
    """
    Webhook delivery log - tracks all webhook attempts
    """
    __tablename__ = "webhook_deliveries"

    delivery_id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, ForeignKey('webhooks.webhook_id', ondelete='CASCADE'), nullable=False)

    # Event details
    event = Column(String(50), nullable=False)  # WebhookEventType value
    payload = Column(JSON, nullable=False)  # Event data

    # Delivery details
    status_code = Column(Integer, nullable=True)  # HTTP status code
    response_body = Column(Text, nullable=True)  # Response from webhook URL
    error_message = Column(Text, nullable=True)  # Error if delivery failed

    # Timing
    delivered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds

    # Retry information
    attempt_number = Column(Integer, default=1, nullable=False)
    success = Column(Boolean, default=False, nullable=False)

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")

    def __repr__(self):
        return f"<WebhookDelivery {self.delivery_id}: {self.event} to webhook {self.webhook_id}>"


class APIKey(Base):
    """
    API Key for programmatic access
    """
    __tablename__ = "api_keys"

    key_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Key details
    key_name = Column(String(255), nullable=False)
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for display (e.g., "gp_abc12...")
    key_hash = Column(String(255), nullable=False)  # SHA256 hash of the full key

    # Status and permissions
    active = Column(Boolean, default=True, nullable=False)
    scopes = Column(JSON, nullable=True)  # List of allowed scopes/permissions

    # Usage tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    usage_count = Column(Integer, default=0, nullable=False)

    # Rate limiting
    rate_limit_per_hour = Column(Integer, default=1000, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<APIKey {self.key_id}: {self.key_name} ({self.key_prefix}...)>"


class IntegrationLog(Base):
    """
    Log of external system integrations (ServiceNow, Jira, Slack, etc.)
    """
    __tablename__ = "integration_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)

    # Integration details
    integration_type = Column(String(50), nullable=False)  # 'servicenow', 'jira', 'slack', etc.
    operation = Column(String(100), nullable=False)  # 'sync_asset', 'create_ticket', 'send_message'

    # Related entities
    asset_id = Column(Integer, ForeignKey('assets.asset_id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    # Request/Response
    request_payload = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)

    # Status
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'pending'
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_ms = Column(Integer, nullable=True)

    # External reference
    external_id = Column(String(255), nullable=True)  # ID in external system
    external_url = Column(String(500), nullable=True)  # Link to external resource

    # Relationships
    asset = relationship("Asset", foreign_keys=[asset_id])
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<IntegrationLog {self.log_id}: {self.integration_type} - {self.operation}>"


class ImportJob(Base):
    """
    Track bulk import jobs (Excel/CSV)
    """
    __tablename__ = "import_jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)

    # Job details
    job_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    import_type = Column(String(50), nullable=False)  # 'assets', 'vendors', 'budgets', etc.

    # Status
    status = Column(String(20), nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    total_rows = Column(Integer, default=0, nullable=False)
    processed_rows = Column(Integer, default=0, nullable=False)
    successful_rows = Column(Integer, default=0, nullable=False)
    failed_rows = Column(Integer, default=0, nullable=False)

    # Validation results
    validation_errors = Column(JSON, nullable=True)  # List of error messages

    # User and timing
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<ImportJob {self.job_id}: {self.job_name} - {self.status}>"
