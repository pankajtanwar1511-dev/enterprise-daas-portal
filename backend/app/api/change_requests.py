"""
Change Request Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1/change-requests", tags=["Change Requests"])


@router.post("/", response_model=schemas.ChangeRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_change_request(
    change_request: schemas.ChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new change request"""

    # Verify asset exists
    asset = db.query(models.Asset).filter(models.Asset.asset_id == change_request.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Create change request
    new_change_request = models.ChangeRequest(
        **change_request.model_dump(),
        requested_by=current_user.user_id
    )

    db.add(new_change_request)
    db.commit()
    db.refresh(new_change_request)

    return new_change_request


@router.get("/", response_model=List[schemas.ChangeRequestResponse])
def list_change_requests(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    approval_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all change requests with optional filters"""
    query = db.query(models.ChangeRequest)

    if asset_id:
        query = query.filter(models.ChangeRequest.asset_id == asset_id)
    if approval_status:
        query = query.filter(models.ChangeRequest.approval_status == approval_status)
    if risk_level:
        query = query.filter(models.ChangeRequest.risk_level == risk_level)
    if status:
        query = query.filter(models.ChangeRequest.status == status)

    change_requests = query.order_by(models.ChangeRequest.requested_at.desc()).offset(skip).limit(limit).all()
    return change_requests


@router.get("/{change_id}", response_model=schemas.ChangeRequestDetailResponse)
def get_change_request(change_id: int, db: Session = Depends(get_db)):
    """Get change request by ID with full details"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    # Get asset details
    asset = db.query(models.Asset).filter(models.Asset.asset_id == change_request.asset_id).first()

    # Get requester details
    requester = db.query(models.User).filter(models.User.user_id == change_request.requested_by).first()

    # Get approver details if exists
    approver = None
    if change_request.approver_id:
        approver = db.query(models.User).filter(models.User.user_id == change_request.approver_id).first()

    return {
        **change_request.__dict__,
        "asset_name": asset.asset_name if asset else None,
        "requester_name": f"{requester.first_name} {requester.last_name}" if requester else None,
        "approver_name": f"{approver.first_name} {approver.last_name}" if approver else None
    }


@router.put("/{change_id}")
async def update_change_request(
    change_id: int,
    change_request_update: schemas.ChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a change request (only if pending)"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    # Only allow editing of pending requests
    if change_request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Cannot edit approved or rejected change requests")

    # Update fields
    for field, value in change_request_update.model_dump(exclude_unset=True).items():
        setattr(change_request, field, value)

    db.commit()
    db.refresh(change_request)

    return change_request


@router.put("/{change_id}/approve")
async def approve_change_request(
    change_id: int,
    approval_comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Approve a change request"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    if change_request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Change request already processed")

    change_request.approval_status = "Approved"
    change_request.approver_id = current_user.user_id
    change_request.approved_at = datetime.utcnow()
    change_request.approval_comments = approval_comments
    change_request.status = "InProgress"

    db.commit()
    db.refresh(change_request)

    return {"message": "Change request approved", "change_request": change_request}


@router.put("/{change_id}/reject")
async def reject_change_request(
    change_id: int,
    approval_comments: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Reject a change request"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    if change_request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Change request already processed")

    change_request.approval_status = "Rejected"
    change_request.approver_id = current_user.user_id
    change_request.approved_at = datetime.utcnow()
    change_request.approval_comments = approval_comments

    db.commit()
    db.refresh(change_request)

    return {"message": "Change request rejected", "change_request": change_request}


@router.put("/{change_id}/complete")
async def complete_change_request(
    change_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Mark a change request as completed"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    if change_request.approval_status != "Approved":
        raise HTTPException(status_code=400, detail="Only approved change requests can be completed")

    change_request.status = "Completed"
    change_request.implementation_date = datetime.utcnow()

    db.commit()
    db.refresh(change_request)

    return {"message": "Change request marked as completed", "change_request": change_request}


@router.get("/stats/summary")
def get_change_request_stats(db: Session = Depends(get_db)):
    """Get change request statistics"""
    from sqlalchemy import func

    total_requests = db.query(func.count(models.ChangeRequest.change_id)).scalar()

    # Count by approval status
    pending = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.approval_status == "Pending"
    ).scalar()

    approved = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.approval_status == "Approved"
    ).scalar()

    rejected = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.approval_status == "Rejected"
    ).scalar()

    # Count by risk level
    critical_risk = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.risk_level == "Critical"
    ).scalar()

    high_risk = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.risk_level == "High"
    ).scalar()

    # Count by status
    in_progress = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.status == "InProgress"
    ).scalar()

    completed = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.status == "Completed"
    ).scalar()

    return {
        "total_requests": total_requests,
        "pending_approval": pending,
        "approved": approved,
        "rejected": rejected,
        "critical_risk": critical_risk,
        "high_risk": high_risk,
        "in_progress": in_progress,
        "completed": completed
    }


@router.delete("/{change_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_change_request(
    change_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a change request (only if pending)"""
    change_request = db.query(models.ChangeRequest).filter(models.ChangeRequest.change_id == change_id).first()
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    # Only allow deletion of pending requests
    if change_request.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Cannot delete approved or rejected change requests")

    db.delete(change_request)
    db.commit()
    return None
