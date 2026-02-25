"""
Team Collaboration Schemas

Pydantic schemas for request/response validation for collaboration features.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== Enums ====================

class TaskPriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TaskStatusEnum(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    IN_REVIEW = "InReview"
    BLOCKED = "Blocked"
    DONE = "Done"
    CANCELLED = "Cancelled"


class NotificationTypeEnum(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    APPROVAL_NEEDED = "approval_needed"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    VIOLATION_DETECTED = "violation_detected"
    SLA_BREACH = "sla_breach"
    COMMENT_MENTION = "comment_mention"
    COMMENT_REPLY = "comment_reply"
    ASSET_UPDATED = "asset_updated"
    INITIATIVE_MILESTONE = "initiative_milestone"


class EntityTypeEnum(str, Enum):
    ASSET = "asset"
    CHANGE_REQUEST = "change_request"
    INITIATIVE = "initiative"
    BUSINESS_GOAL = "business_goal"
    TASK = "task"
    VENDOR = "vendor"
    SLA = "sla"


class ActivityActionEnum(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMMENTED = "commented"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    STATUS_CHANGED = "status_changed"


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to: Optional[int] = Field(None, description="User ID of assignee")
    initiative_id: Optional[int] = Field(None, description="Related initiative ID")
    priority: TaskPriorityEnum = Field(TaskPriorityEnum.MEDIUM, description="Task priority")
    status: TaskStatusEnum = Field(TaskStatusEnum.TODO, description="Task status")
    due_date: Optional[date] = Field(None, description="Due date")
    start_date: Optional[date] = Field(None, description="Start date")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated effort in hours")
    tags: Optional[List[str]] = Field(None, description="Task tags")


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[TaskPriorityEnum] = None
    status: Optional[TaskStatusEnum] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None


class UserInfo(BaseModel):
    """User information for nested responses"""
    user_id: int
    username: str
    full_name: Optional[str]

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Task response schema"""
    task_id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    created_by: int
    initiative_id: Optional[int]
    priority: str
    status: str
    due_date: Optional[str]
    start_date: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str
    estimated_hours: Optional[int]
    actual_hours: Optional[int]
    tags: List[str]
    assignee: Optional[UserInfo]
    creator: UserInfo

    class Config:
        from_attributes = True


# ==================== Notification Schemas ====================

class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    user_id: int = Field(..., description="Recipient user ID")
    type: NotificationTypeEnum = Field(..., description="Notification type")
    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    link: Optional[str] = Field(None, max_length=500, description="Deep link URL")
    entity_type: Optional[EntityTypeEnum] = Field(None, description="Related entity type")
    entity_id: Optional[int] = Field(None, description="Related entity ID")
    priority: TaskPriorityEnum = Field(TaskPriorityEnum.MEDIUM, description="Notification priority")


class NotificationResponse(BaseModel):
    """Notification response schema"""
    notification_id: int
    user_id: int
    type: str
    title: str
    message: str
    link: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[int]
    read: bool
    read_at: Optional[str]
    created_at: str
    priority: str

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: List[int] = Field(..., description="List of notification IDs to mark as read")


# ==================== Comment Schemas ====================

class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    entity_type: EntityTypeEnum = Field(..., description="Entity type being commented on")
    entity_id: int = Field(..., gt=0, description="Entity ID")
    comment_text: str = Field(..., min_length=1, description="Comment text (supports Markdown)")
    parent_comment_id: Optional[int] = Field(None, description="Parent comment ID for replies")
    mentioned_users: Optional[List[int]] = Field(None, description="List of mentioned user IDs")


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    comment_text: str = Field(..., min_length=1, description="Updated comment text")


class CommentResponse(BaseModel):
    """Comment response schema"""
    comment_id: int
    entity_type: str
    entity_id: int
    user_id: int
    comment_text: str
    parent_comment_id: Optional[int]
    mentioned_users: List[int]
    created_at: str
    updated_at: str
    edited: bool
    deleted: bool
    user: UserInfo
    replies: Optional[List['CommentResponse']] = None

    class Config:
        from_attributes = True


# Update forward references
CommentResponse.model_rebuild()


# ==================== Activity Log Schemas ====================

class ActivityLogCreate(BaseModel):
    """Schema for creating an activity log entry"""
    user_id: int = Field(..., description="User who performed the action")
    action: ActivityActionEnum = Field(..., description="Action type")
    entity_type: EntityTypeEnum = Field(..., description="Entity type")
    entity_id: int = Field(..., description="Entity ID")
    entity_name: Optional[str] = Field(None, max_length=255, description="Entity name for display")
    description: str = Field(..., min_length=1, description="Human-readable description")
    metadata: Optional[str] = Field(None, description="Additional metadata (JSON string)")


class ActivityLogResponse(BaseModel):
    """Activity log response schema"""
    activity_id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    entity_name: Optional[str]
    description: str
    metadata: Optional[str]
    created_at: str
    user: UserInfo

    class Config:
        from_attributes = True


# ==================== Team Dashboard Schemas ====================

class TeamDashboardResponse(BaseModel):
    """Team dashboard response schema"""
    assigned_tasks: List[TaskResponse]
    pending_approvals: List[dict]  # Change requests pending approval
    upcoming_deadlines: List[TaskResponse]
    recent_activity: List[ActivityLogResponse]
    team_workload: dict  # User workload statistics


class ActivityFeedFilter(BaseModel):
    """Activity feed filter parameters"""
    entity_type: Optional[EntityTypeEnum] = None
    user_id: Optional[int] = None
    action: Optional[ActivityActionEnum] = None
    limit: int = Field(50, ge=1, le=200, description="Number of activities to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class TaskFilter(BaseModel):
    """Task filter parameters"""
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None
    initiative_id: Optional[int] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    overdue: Optional[bool] = None
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)
