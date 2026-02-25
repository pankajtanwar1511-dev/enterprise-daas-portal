"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class Environment(str, Enum):
    DEV = "DEV"
    QA = "QA"
    UAT = "UAT"
    PROD = "PROD"


class LifecycleStage(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    RETIRED = "Retired"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


# Asset Schemas
class AssetCreate(BaseModel):
    asset_name: str = Field(..., min_length=1, max_length=255)
    domain_id: int
    environment: Environment
    owner_id: int
    version: str
    lifecycle_stage: LifecycleStage = LifecycleStage.DRAFT
    documentation_url: Optional[str] = None
    description: Optional[str] = None
    business_justification: Optional[str] = None
    tags: Optional[str] = None


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    domain_id: Optional[int] = None
    environment: Optional[Environment] = None
    owner_id: Optional[int] = None
    version: Optional[str] = None
    lifecycle_stage: Optional[LifecycleStage] = None
    documentation_url: Optional[str] = None
    description: Optional[str] = None
    business_justification: Optional[str] = None
    tags: Optional[str] = None


class AssetResponse(BaseModel):
    asset_id: int
    asset_name: str
    domain_id: int
    environment: str
    owner_id: int
    version: str
    lifecycle_stage: str
    documentation_url: Optional[str]
    description: Optional[str]
    business_justification: Optional[str] = None
    naming_compliant: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Lifecycle History Schemas
class LifecycleHistoryResponse(BaseModel):
    history_id: int
    asset_id: int
    from_state: Optional[str]
    to_state: str
    change_reason: Optional[str]
    changed_by: int
    changed_at: datetime

    class Config:
        from_attributes = True


# Naming Validation Schemas
class NamingValidationRequest(BaseModel):
    asset_name: str
    exclude_asset_id: Optional[int] = None  # For update validation


class NamingValidationResponse(BaseModel):
    valid: bool
    violations: List[str]
    suggestions: List[str] = []


# Change Request Schemas
class ChangeRequestCreate(BaseModel):
    title: str
    description: str
    asset_id: int
    change_type: str
    risk_level: RiskLevel
    impact_assessment: Optional[str] = None
    rollback_plan: Optional[str] = None


class ChangeRequestResponse(BaseModel):
    change_id: int
    title: str
    asset_id: int
    change_type: str
    risk_level: str
    approval_status: str
    status: str
    requested_at: datetime

    class Config:
        from_attributes = True


class ChangeRequestDetailResponse(BaseModel):
    change_id: int
    title: str
    description: str
    asset_id: int
    asset_name: Optional[str]
    change_type: str
    risk_level: str
    impact_assessment: Optional[str]
    rollback_plan: Optional[str]
    requested_by: int
    requester_name: Optional[str]
    requested_at: datetime
    approval_status: str
    approver_id: Optional[int]
    approver_name: Optional[str]
    approved_at: Optional[datetime]
    approval_comments: Optional[str]
    implementation_date: Optional[datetime]
    status: str
    release_version: Optional[str]

    class Config:
        from_attributes = True


# Compliance Schemas
class ComplianceMetricsResponse(BaseModel):
    total_assets: int
    compliant_assets: int
    compliance_rate: float
    non_compliant_assets: int
    missing_documentation: int
    pending_changes: int


# Domain Schemas
class DomainResponse(BaseModel):
    domain_id: int
    domain_code: str
    domain_name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# User Schemas
class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role_id: int
    is_active: bool

    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    log_id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


# Generic Response
class StandardResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None


# Authentication Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = 4  # Default to Viewer role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class LoginRequest(BaseModel):
    username: str
    password: str
