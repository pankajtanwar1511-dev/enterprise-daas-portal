"""
Notifications API

Endpoints for in-app notification management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User
from ..models_collaboration import Notification
from ..schemas_collaboration import (
    NotificationCreate, NotificationResponse, NotificationMarkRead
)
from .auth import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new notification

    Typically used by system processes or admin users to create notifications.
    Regular users usually receive auto-generated notifications.

    Args:
        notification_data: Notification creation data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Created notification
    """
    try:
        notification = Notification(
            **notification_data.model_dump()
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        logger.info(
            "notification_created",
            notification_id=notification.notification_id,
            user_id=notification.user_id,
            type=notification.type.value
        )

        return notification.to_dict()

    except Exception as e:
        db.rollback()
        logger.error("notification_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List notifications

    Returns notifications ordered by creation date (newest first).
    No authentication required for read access.

    Args:
        user_id: Optional user ID filter
        unread_only: If True, return only unread notifications
        limit: Maximum number of notifications to return
        offset: Offset for pagination
        db: Database session

    Returns:
        List of notifications
    """
    try:
        query = db.query(Notification)

        if user_id is not None:
            query = query.filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.read == False)

        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [notification.to_dict() for notification in notifications]

    except Exception as e:
        logger.error("notification_list_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve notifications: {str(e)}"
        )


@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get unread notifications

    Returns unread notifications ordered by creation date (newest first).
    No authentication required for read access.

    Args:
        user_id: Optional user ID filter
        limit: Maximum number of notifications to return
        offset: Offset for pagination
        db: Database session

    Returns:
        List of unread notifications
    """
    try:
        query = db.query(Notification).filter(Notification.read == False)

        if user_id is not None:
            query = query.filter(Notification.user_id == user_id)

        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [notification.to_dict() for notification in notifications]

    except Exception as e:
        logger.error("unread_notifications_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve unread notifications: {str(e)}"
        )


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications for current user

    Returns:
        Dictionary with unread_count
    """
    try:
        count = db.query(func.count(Notification.notification_id)).filter(
            Notification.user_id == current_user.user_id,
            Notification.read == False
        ).scalar()

        return {"unread_count": count}

    except Exception as e:
        logger.error("unread_count_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a single notification as read

    Args:
        notification_id: Notification ID
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Updated notification

    Raises:
        HTTPException: If notification not found or doesn't belong to user
    """
    try:
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id,
            Notification.user_id == current_user.user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with ID {notification_id} not found"
            )

        notification.read = True
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        logger.info(
            "notification_marked_read",
            notification_id=notification_id,
            user_id=current_user.user_id
        )

        return notification.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("mark_read_failed", error=str(e), notification_id=notification_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for current user

    Args:
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Dictionary with count of marked notifications
    """
    try:
        updated_count = db.query(Notification).filter(
            Notification.user_id == current_user.user_id,
            Notification.read == False
        ).update({
            "read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)

        db.commit()

        logger.info(
            "notifications_marked_all_read",
            user_id=current_user.user_id,
            count=updated_count
        )

        return {"marked_read": updated_count}

    except Exception as e:
        db.rollback()
        logger.error("mark_all_read_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all as read: {str(e)}"
        )


@router.post("/batch-read", status_code=status.HTTP_200_OK)
def mark_batch_read(
    batch: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark multiple notifications as read

    Args:
        batch: List of notification IDs to mark as read
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Dictionary with count of marked notifications
    """
    try:
        updated_count = db.query(Notification).filter(
            Notification.notification_id.in_(batch.notification_ids),
            Notification.user_id == current_user.user_id,
            Notification.read == False
        ).update({
            "read": True,
            "read_at": datetime.utcnow()
        }, synchronize_session=False)

        db.commit()

        logger.info(
            "notifications_batch_marked_read",
            user_id=current_user.user_id,
            count=updated_count
        )

        return {"marked_read": updated_count}

    except Exception as e:
        db.rollback()
        logger.error("batch_mark_read_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark batch as read: {str(e)}"
        )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification

    Args:
        notification_id: Notification ID
        db: Database session
        current_user: Currently authenticated user

    Raises:
        HTTPException: If notification not found or doesn't belong to user
    """
    try:
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id,
            Notification.user_id == current_user.user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with ID {notification_id} not found"
            )

        db.delete(notification)
        db.commit()

        logger.info(
            "notification_deleted",
            notification_id=notification_id,
            user_id=current_user.user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("notification_deletion_failed", error=str(e), notification_id=notification_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )


@router.delete("/clear-all", status_code=status.HTTP_200_OK)
def clear_all_notifications(
    read_only: bool = Query(True, description="Only clear read notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear all notifications for current user

    Args:
        read_only: If True, only delete read notifications (default)
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Dictionary with count of deleted notifications
    """
    try:
        query = db.query(Notification).filter(
            Notification.user_id == current_user.user_id
        )

        if read_only:
            query = query.filter(Notification.read == True)

        deleted_count = query.delete(synchronize_session=False)
        db.commit()

        logger.info(
            "notifications_cleared",
            user_id=current_user.user_id,
            count=deleted_count,
            read_only=read_only
        )

        return {"deleted_count": deleted_count}

    except Exception as e:
        db.rollback()
        logger.error("clear_notifications_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear notifications: {str(e)}"
        )
