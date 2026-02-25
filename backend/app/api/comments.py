"""
Comments API

Endpoints for threaded comment system with @mentions support.
Supports comments on assets, change requests, initiatives, tasks, and more.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User
from ..models_collaboration import (
    Comment, ActivityLog, Notification,
    EntityType, ActivityAction, NotificationType
)
from ..schemas_collaboration import (
    CommentCreate, CommentUpdate, CommentResponse,
    EntityTypeEnum
)
from .auth import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment

    Supports:
    - Top-level comments on entities
    - Threaded replies to other comments
    - @mentions (notifications sent to mentioned users)
    - Markdown formatting

    Args:
        comment_data: Comment creation data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Created comment

    Raises:
        HTTPException: If parent comment not found or validation fails
    """
    try:
        # Validate parent comment exists if provided
        if comment_data.parent_comment_id:
            parent = db.query(Comment).filter(
                Comment.comment_id == comment_data.parent_comment_id
            ).first()

            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent comment with ID {comment_data.parent_comment_id} not found"
                )

            # Ensure parent is on the same entity
            if parent.entity_type != EntityType[comment_data.entity_type.name] or \
               parent.entity_id != comment_data.entity_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment must be on the same entity"
                )

        # Create comment
        comment = Comment(
            entity_type=EntityType[comment_data.entity_type.name],
            entity_id=comment_data.entity_id,
            user_id=current_user.user_id,
            comment_text=comment_data.comment_text,
            parent_comment_id=comment_data.parent_comment_id,
            mentioned_users=",".join(map(str, comment_data.mentioned_users)) if comment_data.mentioned_users else None
        )

        db.add(comment)
        db.flush()  # Get comment_id

        # Create activity log
        activity = ActivityLog(
            user_id=current_user.user_id,
            action=ActivityAction.COMMENTED,
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            entity_name=None,  # Could be enhanced to fetch entity name
            description=f"{current_user.username} commented on {comment.entity_type.value}"
        )
        db.add(activity)

        # Create notifications for mentioned users
        if comment_data.mentioned_users:
            for mentioned_user_id in comment_data.mentioned_users:
                # Skip if mentioning self
                if mentioned_user_id == current_user.user_id:
                    continue

                # Verify user exists
                mentioned_user = db.query(User).filter(User.user_id == mentioned_user_id).first()
                if not mentioned_user:
                    logger.warning(
                        "mention_user_not_found",
                        mentioned_user_id=mentioned_user_id,
                        comment_id=comment.comment_id
                    )
                    continue

                notification = Notification(
                    user_id=mentioned_user_id,
                    type=NotificationType.COMMENT_MENTION,
                    title="You were mentioned in a comment",
                    message=f"{current_user.username} mentioned you in a comment",
                    link=f"/{comment.entity_type.value}s/{comment.entity_id}#comment-{comment.comment_id}",
                    entity_type=comment.entity_type,
                    entity_id=comment.entity_id
                )
                db.add(notification)

        # Create notification for parent comment author (for replies)
        if comment.parent_comment_id:
            parent = db.query(Comment).filter(Comment.comment_id == comment.parent_comment_id).first()
            if parent and parent.user_id != current_user.user_id:
                notification = Notification(
                    user_id=parent.user_id,
                    type=NotificationType.COMMENT_REPLY,
                    title="New reply to your comment",
                    message=f"{current_user.username} replied to your comment",
                    link=f"/{comment.entity_type.value}s/{comment.entity_id}#comment-{comment.comment_id}",
                    entity_type=comment.entity_type,
                    entity_id=comment.entity_id
                )
                db.add(notification)

        db.commit()
        db.refresh(comment)

        logger.info(
            "comment_created",
            comment_id=comment.comment_id,
            entity_type=comment.entity_type.value,
            entity_id=comment.entity_id,
            user_id=current_user.user_id,
            is_reply=comment.parent_comment_id is not None
        )

        return comment.to_dict(include_replies=False)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("comment_creation_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )


@router.get("/", response_model=List[CommentResponse])
def list_comments(
    entity_type: EntityTypeEnum = Query(..., description="Entity type"),
    entity_id: int = Query(..., gt=0, description="Entity ID"),
    include_deleted: bool = Query(False, description="Include soft-deleted comments"),
    include_replies: bool = Query(True, description="Include threaded replies"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List comments for a specific entity

    Returns top-level comments with optional threaded replies.
    Ordered by creation date (oldest first for conversation flow).

    Args:
        entity_type: Type of entity (asset, change_request, etc.)
        entity_id: ID of the entity
        include_deleted: Whether to include soft-deleted comments
        include_replies: Whether to include nested replies
        limit: Maximum number of top-level comments to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of comments (with optional nested replies)
    """
    try:
        query = db.query(Comment).filter(
            Comment.entity_type == EntityType[entity_type.name],
            Comment.entity_id == entity_id,
            Comment.parent_comment_id == None  # Only top-level comments
        )

        if not include_deleted:
            query = query.filter(Comment.deleted == False)

        # Order by creation date (oldest first for conversation flow)
        comments = query.order_by(
            Comment.created_at.asc()
        ).offset(offset).limit(limit).all()

        return [comment.to_dict(include_replies=include_replies) for comment in comments]

    except Exception as e:
        logger.error("comment_list_failed", error=str(e), entity_type=entity_type.value, entity_id=entity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve comments: {str(e)}"
        )


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    include_replies: bool = Query(True, description="Include threaded replies"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single comment by ID

    Args:
        comment_id: Comment ID
        include_replies: Whether to include nested replies
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Comment details (with optional nested replies)

    Raises:
        HTTPException: If comment not found
    """
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )

    return comment.to_dict(include_replies=include_replies)


@router.get("/{comment_id}/replies", response_model=List[CommentResponse])
def get_comment_replies(
    comment_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted replies"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all replies to a specific comment

    Args:
        comment_id: Parent comment ID
        include_deleted: Whether to include soft-deleted replies
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of reply comments

    Raises:
        HTTPException: If parent comment not found
    """
    # Verify parent comment exists
    parent = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )

    try:
        query = db.query(Comment).filter(
            Comment.parent_comment_id == comment_id
        )

        if not include_deleted:
            query = query.filter(Comment.deleted == False)

        replies = query.order_by(Comment.created_at.asc()).all()

        return [reply.to_dict(include_replies=False) for reply in replies]

    except Exception as e:
        logger.error("comment_replies_failed", error=str(e), comment_id=comment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve replies: {str(e)}"
        )


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment

    Only the comment author can edit their own comments.
    Marks comment as edited and updates timestamp.

    Args:
        comment_id: Comment ID
        comment_update: Updated comment data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Updated comment

    Raises:
        HTTPException: If comment not found or user not authorized
    """
    try:
        comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found"
            )

        # Check authorization - only comment author can edit
        if comment.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments"
            )

        # Check if comment is deleted
        if comment.deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit deleted comment"
            )

        # Update comment text
        comment.comment_text = comment_update.comment_text
        comment.edited = True
        comment.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(comment)

        logger.info(
            "comment_updated",
            comment_id=comment_id,
            user_id=current_user.user_id
        )

        return comment.to_dict(include_replies=False)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("comment_update_failed", error=str(e), comment_id=comment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}"
        )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a comment

    Only the comment author can delete their own comments.
    Comments are soft-deleted (marked as deleted, not removed from database).

    Args:
        comment_id: Comment ID
        db: Database session
        current_user: Currently authenticated user

    Raises:
        HTTPException: If comment not found or user not authorized
    """
    try:
        comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found"
            )

        # Check authorization - only comment author can delete
        if comment.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments"
            )

        # Soft delete
        comment.deleted = True
        comment.deleted_at = datetime.utcnow()
        comment.comment_text = "[This comment has been deleted]"

        db.commit()

        logger.info(
            "comment_deleted",
            comment_id=comment_id,
            user_id=current_user.user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("comment_deletion_failed", error=str(e), comment_id=comment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[CommentResponse])
def get_user_comments(
    user_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted comments"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments by a specific user

    Useful for user profile pages or activity tracking.

    Args:
        user_id: User ID
        include_deleted: Whether to include soft-deleted comments
        limit: Maximum number of comments to return
        offset: Offset for pagination
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of user's comments
    """
    try:
        query = db.query(Comment).filter(Comment.user_id == user_id)

        if not include_deleted:
            query = query.filter(Comment.deleted == False)

        comments = query.order_by(
            Comment.created_at.desc()
        ).offset(offset).limit(limit).all()

        return [comment.to_dict(include_replies=False) for comment in comments]

    except Exception as e:
        logger.error("user_comments_failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user comments: {str(e)}"
        )


@router.get("/recent", response_model=List[CommentResponse])
def get_recent_comments(
    entity_type: Optional[EntityTypeEnum] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent comments across all entities

    Useful for activity feeds and dashboards.

    Args:
        entity_type: Optional filter by entity type
        limit: Maximum number of comments to return
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List of recent comments
    """
    try:
        query = db.query(Comment).filter(Comment.deleted == False)

        if entity_type:
            query = query.filter(Comment.entity_type == EntityType[entity_type.name])

        comments = query.order_by(
            Comment.created_at.desc()
        ).limit(limit).all()

        return [comment.to_dict(include_replies=False) for comment in comments]

    except Exception as e:
        logger.error("recent_comments_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent comments: {str(e)}"
        )
