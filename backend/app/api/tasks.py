"""
Tasks API

Endpoints for task assignment and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..database import get_db
from ..models import User
from ..models_collaboration import Task, TaskStatus, TaskPriority, ActivityLog, ActivityAction, EntityType, Notification, NotificationType
from ..schemas_collaboration import (
    TaskCreate, TaskUpdate, TaskResponse, TaskFilter,
    TaskStatusEnum, TaskPriorityEnum
)
from .auth import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task

    Args:
        task_data: Task creation data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Created task

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Validate assignee exists if provided
        if task_data.assigned_to:
            assignee = db.query(User).filter(User.user_id == task_data.assigned_to).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {task_data.assigned_to} not found"
                )

        # Create task
        task = Task(
            title=task_data.title,
            description=task_data.description,
            assigned_to=task_data.assigned_to,
            created_by=current_user.user_id,
            initiative_id=task_data.initiative_id,
            priority=TaskPriority[task_data.priority.name],
            status=TaskStatus[task_data.status.name],
            due_date=task_data.due_date,
            start_date=task_data.start_date,
            estimated_hours=task_data.estimated_hours,
            tags=",".join(task_data.tags) if task_data.tags else None
        )

        db.add(task)
        db.flush()  # Get task_id

        # Create activity log
        activity = ActivityLog(
            user_id=current_user.user_id,
            action=ActivityAction.CREATED,
            entity_type=EntityType.TASK,
            entity_id=task.task_id,
            entity_name=task.title,
            description=f"{current_user.username} created task: {task.title}"
        )
        db.add(activity)

        # Create notification for assignee if different from creator
        if task.assigned_to and task.assigned_to != current_user.user_id:
            notification = Notification(
                user_id=task.assigned_to,
                type=NotificationType.TASK_ASSIGNED,
                title="New Task Assigned",
                message=f"{current_user.username} assigned you the task: {task.title}",
                link=f"/tasks/{task.task_id}",
                entity_type=EntityType.TASK,
                entity_id=task.task_id
            )
            db.add(notification)

        db.commit()
        db.refresh(task)

        logger.info(
            "task_created",
            task_id=task.task_id,
            title=task.title,
            created_by=current_user.user_id,
            assigned_to=task.assigned_to
        )

        return task.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("task_creation_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    assigned_to: Optional[int] = Query(None, description="Filter by assignee user ID"),
    created_by: Optional[int] = Query(None, description="Filter by creator user ID"),
    initiative_id: Optional[int] = Query(None, description="Filter by initiative ID"),
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriorityEnum] = Query(None, description="Filter by priority"),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks with optional filters

    Returns tasks visible to the current user based on filters.
    """
    try:
        query = db.query(Task)

        # Apply filters
        if assigned_to is not None:
            query = query.filter(Task.assigned_to == assigned_to)

        if created_by is not None:
            query = query.filter(Task.created_by == created_by)

        if initiative_id is not None:
            query = query.filter(Task.initiative_id == initiative_id)

        if status is not None:
            query = query.filter(Task.status == TaskStatus[status.name])

        if priority is not None:
            query = query.filter(Task.priority == TaskPriority[priority.name])

        if overdue:
            today = date.today()
            query = query.filter(
                Task.due_date < today,
                Task.status != TaskStatus.DONE,
                Task.status != TaskStatus.CANCELLED
            )

        # Order by due date, then priority
        query = query.order_by(
            Task.due_date.asc().nullslast(),
            Task.priority.desc(),
            Task.created_at.desc()
        )

        # Pagination
        tasks = query.offset(offset).limit(limit).all()

        return [task.to_dict() for task in tasks]

    except Exception as e:
        logger.error("task_list_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task by ID

    Args:
        task_id: Task ID
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Task details

    Raises:
        HTTPException: If task not found
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return task.to_dict()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task

    Args:
        task_id: Task ID
        task_update: Update data
        db: Database session
        current_user: Currently authenticated user

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found or update fails
    """
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        # Track changes for activity log
        changes = []
        old_status = task.status

        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "tags" and value is not None:
                value = ",".join(value)
            elif field == "priority" and value is not None:
                value = TaskPriority[value.name]
                changes.append(f"priority changed to {value.value}")
            elif field == "status" and value is not None:
                value = TaskStatus[value.name]
                if old_status != value:
                    changes.append(f"status changed from {old_status.value} to {value.value}")
            elif field == "assigned_to" and value is not None and value != task.assigned_to:
                changes.append(f"reassigned to user {value}")

            setattr(task, field, value)

        # Mark as completed if status changed to Done
        if task.status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            task.completed_at = datetime.utcnow()

        db.flush()

        # Create activity log
        if changes:
            activity = ActivityLog(
                user_id=current_user.user_id,
                action=ActivityAction.UPDATED,
                entity_type=EntityType.TASK,
                entity_id=task.task_id,
                entity_name=task.title,
                description=f"{current_user.username} updated task: {', '.join(changes)}"
            )
            db.add(activity)

            # Notify assignee of updates
            if task.assigned_to and task.assigned_to != current_user.user_id:
                notification = Notification(
                    user_id=task.assigned_to,
                    type=NotificationType.TASK_UPDATED,
                    title="Task Updated",
                    message=f"{current_user.username} updated your task: {task.title}",
                    link=f"/tasks/{task.task_id}",
                    entity_type=EntityType.TASK,
                    entity_id=task.task_id
                )
                db.add(notification)

        # Notify assignee and creator when task completed
        if task.status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            for user_id in [task.assigned_to, task.created_by]:
                if user_id and user_id != current_user.user_id:
                    notification = Notification(
                        user_id=user_id,
                        type=NotificationType.TASK_COMPLETED,
                        title="Task Completed",
                        message=f"{current_user.username} marked task as complete: {task.title}",
                        link=f"/tasks/{task.task_id}",
                        entity_type=EntityType.TASK,
                        entity_id=task.task_id
                    )
                    db.add(notification)

        db.commit()
        db.refresh(task)

        logger.info(
            "task_updated",
            task_id=task.task_id,
            updated_by=current_user.user_id,
            changes=changes
        )

        return task.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("task_update_failed", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete task

    Args:
        task_id: Task ID
        db: Database session
        current_user: Currently authenticated user

    Raises:
        HTTPException: If task not found
    """
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        # Create activity log before deletion
        activity = ActivityLog(
            user_id=current_user.user_id,
            action=ActivityAction.DELETED,
            entity_type=EntityType.TASK,
            entity_id=task.task_id,
            entity_name=task.title,
            description=f"{current_user.username} deleted task: {task.title}"
        )
        db.add(activity)

        db.delete(task)
        db.commit()

        logger.info(
            "task_deleted",
            task_id=task_id,
            deleted_by=current_user.user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("task_deletion_failed", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@router.get("/my/tasks", response_model=List[TaskResponse])
def get_my_tasks(
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tasks assigned to current user

    Convenience endpoint to get user's assigned tasks.
    """
    try:
        query = db.query(Task).filter(Task.assigned_to == current_user.user_id)

        if status:
            query = query.filter(Task.status == TaskStatus[status.name])

        tasks = query.order_by(
            Task.due_date.asc().nullslast(),
            Task.priority.desc()
        ).all()

        return [task.to_dict() for task in tasks]

    except Exception as e:
        logger.error("my_tasks_failed", error=str(e), user_id=current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )
