"""
Audit Logs API Routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/v1/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g., Asset, User, Domain)"),
    action: Optional[str] = Query(None, description="Filter by action (e.g., CREATE, UPDATE, DELETE)"),
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs until this date"),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering

    Filters:
    - user_id: Show only logs for specific user
    - entity_type: Show only logs for specific entity type (Asset, User, Domain, etc.)
    - action: Show only specific actions (CREATE, UPDATE, DELETE, LOGIN, etc.)
    - start_date: Show logs from this date onwards
    - end_date: Show logs up to this date
    """
    query = db.query(models.AuditLog)

    # Apply filters
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(models.AuditLog.action == action)
    if start_date:
        query = query.filter(models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(models.AuditLog.timestamp <= end_date)

    # Order by most recent first
    logs = query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    return logs


@router.get("/stats")
def get_audit_stats(db: Session = Depends(get_db)):
    """
    Get audit log statistics

    Returns summary statistics like:
    - Total log count
    - Logs by action type
    - Logs by entity type
    - Most active users
    """
    from sqlalchemy import func

    total_logs = db.query(func.count(models.AuditLog.log_id)).scalar()

    # Count by action
    actions_count = (
        db.query(models.AuditLog.action, func.count(models.AuditLog.log_id))
        .group_by(models.AuditLog.action)
        .all()
    )

    # Count by entity type
    entities_count = (
        db.query(models.AuditLog.entity_type, func.count(models.AuditLog.log_id))
        .group_by(models.AuditLog.entity_type)
        .all()
    )

    # Most active users (top 5)
    top_users = (
        db.query(
            models.AuditLog.user_id,
            models.User.username,
            func.count(models.AuditLog.log_id).label("activity_count")
        )
        .join(models.User, models.AuditLog.user_id == models.User.user_id)
        .group_by(models.AuditLog.user_id, models.User.username)
        .order_by(func.count(models.AuditLog.log_id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_logs": total_logs,
        "by_action": [{"action": action, "count": count} for action, count in actions_count],
        "by_entity_type": [{"entity_type": entity, "count": count} for entity, count in entities_count],
        "top_users": [
            {"user_id": user_id, "username": username, "activity_count": count}
            for user_id, username, count in top_users
        ]
    }


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[schemas.AuditLogResponse])
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all audit logs for a specific entity

    Useful for viewing complete change history of a single asset, user, domain, etc.
    """
    logs = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.entity_type == entity_type,
            models.AuditLog.entity_id == entity_id
        )
        .order_by(models.AuditLog.timestamp.desc())
        .all()
    )

    return logs
