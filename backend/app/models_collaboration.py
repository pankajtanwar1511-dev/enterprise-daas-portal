"""
Team Collaboration Models

This module contains models for team collaboration features:
- Task Assignment System
- In-App Notifications
- Comment System
- Activity Tracking
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


# ==================== Enums ====================

class TaskPriority(str, enum.Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TaskStatus(str, enum.Enum):
    """Task status"""
    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    IN_REVIEW = "InReview"
    BLOCKED = "Blocked"
    DONE = "Done"
    CANCELLED = "Cancelled"


class NotificationType(str, enum.Enum):
    """Notification types"""
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


class EntityType(str, enum.Enum):
    """Entity types for comments and activity"""
    ASSET = "asset"
    CHANGE_REQUEST = "change_request"
    INITIATIVE = "initiative"
    BUSINESS_GOAL = "business_goal"
    TASK = "task"
    VENDOR = "vendor"
    SLA = "sla"


class ActivityAction(str, enum.Enum):
    """Activity action types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMMENTED = "commented"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    STATUS_CHANGED = "status_changed"


# ==================== Models ====================

class Task(Base):
    """
    Task Assignment Model

    Enables task assignment and tracking for team collaboration.
    Tasks can be linked to strategic initiatives or standalone.
    """
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Linkage (optional - can be standalone or linked to initiative)
    initiative_id = Column(Integer, ForeignKey("strategic_initiatives.initiative_id"), nullable=True)

    # Task properties
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)

    # Dates
    due_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Effort estimation (in hours)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)

    # Tags (comma-separated)
    tags = Column(String(500), nullable=True)

    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by], backref="created_tasks")
    initiative = relationship("StrategicInitiative", backref="tasks")
    comments = relationship("Comment",
                          primaryjoin="and_(Task.task_id==foreign(Comment.entity_id), Comment.entity_type=='task')",
                          viewonly=True)

    def to_dict(self):
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "initiative_id": self.initiative_id,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "tags": self.tags.split(",") if self.tags else [],
            "assignee": {
                "user_id": self.assignee.user_id,
                "username": self.assignee.username,
                "full_name": self.assignee.full_name
            } if self.assignee else None,
            "creator": {
                "user_id": self.creator.user_id,
                "username": self.creator.username,
                "full_name": self.creator.full_name
            } if self.creator else None,
        }


class Notification(Base):
    """
    In-App Notification Model

    Provides real-time notifications to users about important events:
    - Task assignments and updates
    - Approval requests and decisions
    - Compliance violations
    - SLA breaches
    - Comments and mentions
    """
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    # Notification content
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Deep link to related entity
    link = Column(String(500), nullable=True)

    # Related entity (optional)
    entity_type = Column(Enum(EntityType), nullable=True)
    entity_id = Column(Integer, nullable=True)

    # Status
    read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Priority (affects display order and styling)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

    # Relationships
    user = relationship("User", backref="notifications")

    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "type": self.type.value if self.type else None,
            "title": self.title,
            "message": self.message,
            "link": self.link,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entity_id": self.entity_id,
            "read": self.read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "priority": self.priority.value if self.priority else None,
        }


class Comment(Base):
    """
    Comment System Model

    Enables threaded discussions on various entities:
    - Assets
    - Change Requests
    - Strategic Initiatives
    - Business Goals
    - Tasks

    Supports:
    - Threaded replies
    - @mentions (stored in mentioned_users field)
    - Markdown formatting
    - Edit history
    """
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)

    # Entity being commented on
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    # Comment author
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Comment content
    comment_text = Column(Text, nullable=False)

    # Threading support
    parent_comment_id = Column(Integer, ForeignKey("comments.comment_id"), nullable=True)

    # Mentions (comma-separated user IDs)
    mentioned_users = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)

    # Soft delete
    deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="comments")
    parent = relationship("Comment", remote_side=[comment_id], backref="replies")

    # Entity relationships (optional - for eager loading)
    asset = relationship("Asset", foreign_keys="Comment.entity_id",
                        primaryjoin="and_(Comment.entity_type=='asset', foreign(Comment.entity_id)==Asset.asset_id)",
                        uselist=False, viewonly=True)
    change_request = relationship("ChangeRequest", foreign_keys="Comment.entity_id",
                                 primaryjoin="and_(Comment.entity_type=='change_request', foreign(Comment.entity_id)==ChangeRequest.change_id)",
                                 uselist=False, viewonly=True)
    initiative = relationship("StrategicInitiative", foreign_keys="Comment.entity_id",
                            primaryjoin="and_(Comment.entity_type=='initiative', foreign(Comment.entity_id)==StrategicInitiative.initiative_id)",
                            uselist=False, viewonly=True)
    task = relationship("Task", foreign_keys="Comment.entity_id",
                       primaryjoin="and_(Comment.entity_type=='task', foreign(Comment.entity_id)==Task.task_id)",
                       uselist=False, viewonly=True)

    def to_dict(self, include_replies=False):
        """Convert comment to dictionary"""
        result = {
            "comment_id": self.comment_id,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entity_id": self.entity_id,
            "user_id": self.user_id,
            "comment_text": self.comment_text,
            "parent_comment_id": self.parent_comment_id,
            "mentioned_users": [int(uid) for uid in self.mentioned_users.split(",")] if self.mentioned_users else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "edited": self.edited,
            "deleted": self.deleted,
            "user": {
                "user_id": self.user.user_id,
                "username": self.user.username,
                "full_name": self.user.full_name
            } if self.user else None,
        }

        if include_replies and self.replies:
            result["replies"] = [reply.to_dict(include_replies=False) for reply in self.replies if not reply.deleted]

        return result


class ActivityLog(Base):
    """
    Activity Log Model

    Tracks all user activities for the activity feed:
    - Entity creations, updates, deletions
    - Status changes
    - Assignments
    - Approvals
    - Comments

    This provides a comprehensive audit trail and powers the activity feed UI.
    """
    __tablename__ = "activity_logs"

    activity_id = Column(Integer, primary_key=True, index=True)

    # Actor
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    # Action
    action = Column(Enum(ActivityAction), nullable=False)

    # Entity
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    entity_name = Column(String(255), nullable=True)  # For display purposes

    # Description (human-readable)
    description = Column(Text, nullable=False)

    # Additional metadata (JSON-like, stored as text)
    meta_data = Column(Text, nullable=True)  # e.g., "{'old_status': 'Todo', 'new_status': 'Done'}"

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="activities")

    def to_dict(self):
        """Convert activity to dictionary"""
        return {
            "activity_id": self.activity_id,
            "user_id": self.user_id,
            "action": self.action.value if self.action else None,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "description": self.description,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user": {
                "user_id": self.user.user_id,
                "username": self.user.username,
                "full_name": self.user.full_name
            } if self.user else None,
        }
