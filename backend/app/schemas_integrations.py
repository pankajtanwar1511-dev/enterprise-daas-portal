"""
Pydantic schemas for Phase 3 integrations
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WebhookEventType(str, Enum):
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


# Webhook Schemas
class WebhookCreate(BaseModel):
    """Schema for creating a webhook"""
    name: str = Field(..., min_length=1, max_length=255, description="Webhook name")
    url: HttpUrl = Field(..., description="Webhook URL endpoint")
    events: List[WebhookEventType] = Field(..., min_items=1, description="Events to subscribe to")
    retry_count: int = Field(3, ge=0, le=10, description="Number of retries on failure")
    timeout_seconds: int = Field(10, ge=1, le=60, description="Request timeout in seconds")


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[HttpUrl] = None
    events: Optional[List[WebhookEventType]] = Field(None, min_items=1)
    active: Optional[bool] = None
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=60)


class WebhookResponse(BaseModel):
    """Schema for webhook response"""
    webhook_id: int
    name: str
    url: str
    events: List[str]
    active: bool
    created_at: datetime
    last_triggered: Optional[datetime]
    retry_count: int
    timeout_seconds: int

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery log"""
    delivery_id: int
    webhook_id: int
    event: str
    status_code: Optional[int]
    success: bool
    delivered_at: datetime
    duration_ms: Optional[int]
    attempt_number: int
    error_message: Optional[str]

    class Config:
        from_attributes = True


class WebhookTestRequest(BaseModel):
    """Schema for testing a webhook"""
    event: WebhookEventType
    test_payload: Optional[Dict[str, Any]] = None


# API Key Schemas
class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    key_name: str = Field(..., min_length=1, max_length=255, description="API key name")
    scopes: Optional[List[str]] = Field(None, description="Allowed scopes/permissions")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Days until expiration")
    rate_limit_per_hour: int = Field(1000, ge=10, le=10000, description="Rate limit per hour")


class APIKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)"""
    key_id: int
    key_name: str
    key_prefix: str
    active: bool
    scopes: Optional[List[str]]
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    usage_count: int
    rate_limit_per_hour: int

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(BaseModel):
    """Schema for newly created API key (includes the actual key - only shown once)"""
    key_id: int
    key_name: str
    api_key: str  # Full key - only returned on creation
    key_prefix: str
    scopes: Optional[List[str]]
    created_at: datetime
    expires_at: Optional[datetime]

    message: str = "Save this API key now. You won't be able to see it again!"


# Integration Log Schemas
class IntegrationLogResponse(BaseModel):
    """Schema for integration log"""
    log_id: int
    integration_type: str
    operation: str
    status: str
    created_at: datetime
    duration_ms: Optional[int]
    external_id: Optional[str]
    external_url: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# Import Job Schemas
class ImportJobCreate(BaseModel):
    """Schema for creating an import job"""
    job_name: str = Field(..., min_length=1, max_length=255)
    import_type: str = Field(..., description="Type of data to import (assets, vendors, etc.)")
    file_name: str


class ImportJobResponse(BaseModel):
    """Schema for import job response"""
    job_id: int
    job_name: str
    file_name: str
    import_type: str
    status: str
    total_rows: int
    processed_rows: int
    successful_rows: int
    failed_rows: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    validation_errors: Optional[List[Dict[str, Any]]]

    class Config:
        from_attributes = True


# Slack Integration Schemas
class SlackMessageRequest(BaseModel):
    """Schema for sending Slack message"""
    channel: str = Field(..., description="Slack channel name or ID")
    message: str = Field(..., min_length=1, description="Message to send")
    blocks: Optional[List[Dict[str, Any]]] = Field(None, description="Slack message blocks")


class SlackNotificationSettings(BaseModel):
    """Schema for Slack notification settings"""
    enabled: bool = True
    webhook_url: Optional[str] = None
    default_channel: str = Field("#governance-alerts", description="Default channel for notifications")
    notify_on: List[WebhookEventType] = Field(default_factory=list, description="Events to notify on")


# ServiceNow Integration Schemas
class ServiceNowAssetSync(BaseModel):
    """Schema for syncing asset to ServiceNow"""
    asset_id: int
    sync_type: str = Field("full", description="Sync type: full or partial")


class ServiceNowTicketCreate(BaseModel):
    """Schema for creating ServiceNow ticket"""
    short_description: str
    description: str
    category: str = "Data Governance"
    urgency: int = Field(3, ge=1, le=3, description="1=High, 2=Medium, 3=Low")
    asset_id: Optional[int] = None


class ServiceNowResponse(BaseModel):
    """Schema for ServiceNow operation response"""
    success: bool
    sys_id: Optional[str] = None
    number: Optional[str] = None
    url: Optional[str] = None
    message: str
