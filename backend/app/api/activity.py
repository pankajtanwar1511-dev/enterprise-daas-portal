"""
Activity Feed API

Endpoints for activity tracking and feed display.
Provides comprehensive activity stream for users and entities.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User
from ..models_collaboration import ActivityLog, EntityType, ActivityAction
from ..schemas_collaboration import (
    ActivityLogResponse, ActivityFeedFilter,
    EntityTypeEnum, ActivityActionEnum
)
from .auth import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/activity", tags=["activity"])


@router.get("/", response_model=List[ActivityLogResponse])
def get_activity_feed(
    entity_type: Optional[EntityTypeEnum] = Query(None, description="Filter by entity type"),
    user_id: Optional[int] = Query(None, description="Filter by user who performed action"),
    action: Optional[ActivityActionEnum] = Query(None, description="Filter by action type"),
    entity_id: Optional[int] = Query(None, description="Filter by specific entity ID (requires entity_type)"),
    days: Optional[int] = Query(None, ge=1, le=90, description="Filter to last N days"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of activities to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity feed with optional filters

    Returns activities ordered by creation date (newest first).
    Useful for dashboards, audit trails, and activity streams.

    Args:
        entity_type: Filter by entity type (asset, task, etc.)
        user_id: Filter by user who performed the action
        action: Filter by action type (created, updated, etc.)
        entity_id: Filter by specific entity ID (must provide entity_type)
        days: Show only activities from last N days
        limit: Maximum number of activities to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of activities
    """
    try:
        query = db.query(ActivityLog)

        # Apply filters
        if entity_type is not None:
            query = query.filter(ActivityLog.entity_type == EntityType[entity_type.name])

        if user_id is not None:
            query = query.filter(ActivityLog.user_id == user_id)

        if action is not None:
            query = query.filter(ActivityLog.action == ActivityAction[action.name])

        if entity_id is not None:
            if entity_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="entity_type is required when filtering by entity_id"
                )
            query = query.filter(ActivityLog.entity_id == entity_id)

        if days is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityLog.created_at >= cutoff_date)

        # Order by creation date (newest first)
        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [activity.to_dict() for activity in activities]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("activity_feed_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve activity feed: {str(e)}"
        )


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[ActivityLogResponse])
def get_entity_activity(
    entity_type: EntityTypeEnum,
    entity_id: int,
    action: Optional[ActivityActionEnum] = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all activity for a specific entity

    Useful for displaying audit trail on entity detail pages.

    Args:
        entity_type: Entity type (asset, change_request, etc.)
        entity_id: Entity ID
        action: Optional filter by action type
        limit: Maximum number of activities to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of activities for the entity
    """
    try:
        query = db.query(ActivityLog).filter(
            ActivityLog.entity_type == EntityType[entity_type.name],
            ActivityLog.entity_id == entity_id
        )

        if action is not None:
            query = query.filter(ActivityLog.action == ActivityAction[action.name])

        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [activity.to_dict() for activity in activities]

    except Exception as e:
        logger.error(
            "entity_activity_failed",
            error=str(e),
            entity_type=entity_type.value,
            entity_id=entity_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entity activity: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[ActivityLogResponse])
def get_user_activity(
    user_id: int,
    entity_type: Optional[EntityTypeEnum] = Query(None, description="Filter by entity type"),
    action: Optional[ActivityActionEnum] = Query(None, description="Filter by action type"),
    days: Optional[int] = Query(None, ge=1, le=90, description="Filter to last N days"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all activities by a specific user

    Useful for user profile pages and productivity tracking.

    Args:
        user_id: User ID
        entity_type: Optional filter by entity type
        action: Optional filter by action type
        days: Show only activities from last N days
        limit: Maximum number of activities to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of user's activities
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        query = db.query(ActivityLog).filter(ActivityLog.user_id == user_id)

        if entity_type is not None:
            query = query.filter(ActivityLog.entity_type == EntityType[entity_type.name])

        if action is not None:
            query = query.filter(ActivityLog.action == ActivityAction[action.name])

        if days is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityLog.created_at >= cutoff_date)

        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [activity.to_dict() for activity in activities]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_activity_failed", error=str(e), target_user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user activity: {str(e)}"
        )


@router.get("/recent", response_model=List[ActivityLogResponse])
def get_recent_activity(
    entity_type: Optional[EntityTypeEnum] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100, description="Number of recent activities"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent activities across the platform

    Provides a real-time activity stream for dashboards.
    Optimized for quick loading with lower limits.

    Args:
        entity_type: Optional filter by entity type
        limit: Number of recent activities to return (default 20, max 100)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of recent activities
    """
    try:
        query = db.query(ActivityLog)

        if entity_type is not None:
            query = query.filter(ActivityLog.entity_type == EntityType[entity_type.name])

        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).limit(limit).all()

        return [activity.to_dict() for activity in activities]

    except Exception as e:
        logger.error("recent_activity_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        )


@router.get("/my-activity", response_model=List[ActivityLogResponse])
def get_my_activity(
    entity_type: Optional[EntityTypeEnum] = Query(None, description="Filter by entity type"),
    action: Optional[ActivityActionEnum] = Query(None, description="Filter by action type"),
    days: Optional[int] = Query(7, ge=1, le=90, description="Show last N days (default 7)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's own activity

    Convenience endpoint for "My Activity" pages.

    Args:
        entity_type: Optional filter by entity type
        action: Optional filter by action type
        days: Show activities from last N days (default 7)
        limit: Maximum number of activities to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of current user's activities
    """
    try:
        query = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.user_id)

        if entity_type is not None:
            query = query.filter(ActivityLog.entity_type == EntityType[entity_type.name])

        if action is not None:
            query = query.filter(ActivityLog.action == ActivityAction[action.name])

        if days is not None:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ActivityLog.created_at >= cutoff_date)

        activities = query.order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [activity.to_dict() for activity in activities]

    except Exception as e:
        logger.error("my_activity_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve your activity: {str(e)}"
        )


@router.get("/stats", response_model=dict)
def get_activity_stats(
    days: int = Query(30, ge=1, le=365, description="Calculate stats for last N days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity statistics

    Provides aggregated stats for dashboards and reports:
    - Total activities by action type
    - Most active users
    - Most active entities

    Args:
        days: Calculate statistics for last N days (default 30)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Dictionary with activity statistics
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total activities by action
        from sqlalchemy import func
        action_counts = db.query(
            ActivityLog.action,
            func.count(ActivityLog.activity_id).label('count')
        ).filter(
            ActivityLog.created_at >= cutoff_date
        ).group_by(ActivityLog.action).all()

        # Total activities by entity type
        entity_counts = db.query(
            ActivityLog.entity_type,
            func.count(ActivityLog.activity_id).label('count')
        ).filter(
            ActivityLog.created_at >= cutoff_date
        ).group_by(ActivityLog.entity_type).all()

        # Most active users (top 10)
        active_users = db.query(
            ActivityLog.user_id,
            func.count(ActivityLog.activity_id).label('count')
        ).filter(
            ActivityLog.created_at >= cutoff_date
        ).group_by(ActivityLog.user_id).order_by(
            func.count(ActivityLog.activity_id).desc()
        ).limit(10).all()

        # Total activities
        total_activities = db.query(func.count(ActivityLog.activity_id)).filter(
            ActivityLog.created_at >= cutoff_date
        ).scalar()

        return {
            "period_days": days,
            "total_activities": total_activities,
            "by_action": [
                {"action": action.value if action else None, "count": count}
                for action, count in action_counts
            ],
            "by_entity_type": [
                {"entity_type": entity_type.value if entity_type else None, "count": count}
                for entity_type, count in entity_counts
            ],
            "top_users": [
                {"user_id": user_id, "activity_count": count}
                for user_id, count in active_users
            ]
        }

    except Exception as e:
        logger.error("activity_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate activity statistics: {str(e)}"
        )


@router.get("/timeline/{entity_type}/{entity_id}", response_model=dict)
def get_entity_timeline(
    entity_type: EntityTypeEnum,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a timeline view of entity activity

    Groups activities by date for timeline visualization.

    Args:
        entity_type: Entity type
        entity_id: Entity ID
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Dictionary with timeline data grouped by date
    """
    try:
        from sqlalchemy import func, cast, Date

        # Get all activities for the entity
        activities = db.query(ActivityLog).filter(
            ActivityLog.entity_type == EntityType[entity_type.name],
            ActivityLog.entity_id == entity_id
        ).order_by(ActivityLog.created_at.asc()).all()

        # Group by date
        timeline = {}
        for activity in activities:
            activity_date = activity.created_at.date().isoformat()
            if activity_date not in timeline:
                timeline[activity_date] = []
            timeline[activity_date].append(activity.to_dict())

        return {
            "entity_type": entity_type.value,
            "entity_id": entity_id,
            "timeline": timeline,
            "total_activities": len(activities)
        }

    except Exception as e:
        logger.error(
            "timeline_failed",
            error=str(e),
            entity_type=entity_type.value,
            entity_id=entity_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate timeline: {str(e)}"
        )
