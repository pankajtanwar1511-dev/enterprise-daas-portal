"""
Stakeholders API
Endpoints for managing business stakeholders and their data needs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models_extended import Stakeholder

router = APIRouter(prefix="/api/v1/stakeholders", tags=["stakeholders"])


@router.get("/", response_model=List[dict])
def list_stakeholders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List all stakeholders

    Returns stakeholder information including:
    - Basic info (name, role, department)
    - Contact details
    - Engagement level and influence

    No authentication required for read access.
    """
    stakeholders = db.query(Stakeholder).offset(skip).limit(limit).all()

    return [
        {
            "stakeholder_id": s.stakeholder_id,
            "stakeholder_name": s.name,
            "role": s.title,
            "department": s.department,
            "email": s.email,
            "phone": s.phone,
            "engagement_level": s.engagement_level,
            "influence_level": s.influence_level,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in stakeholders
    ]


@router.get("/{stakeholder_id}", response_model=dict)
def get_stakeholder(
    stakeholder_id: int,
    db: Session = Depends(get_db)
):
    """
    Get stakeholder by ID

    Returns detailed stakeholder information including all fields.
    No authentication required for read access.
    """
    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.stakeholder_id == stakeholder_id
    ).first()

    if not stakeholder:
        raise HTTPException(
            status_code=404,
            detail=f"Stakeholder with ID {stakeholder_id} not found"
        )

    return {
        "stakeholder_id": stakeholder.stakeholder_id,
        "stakeholder_name": stakeholder.name,
        "role": stakeholder.title,
        "department": stakeholder.department,
        "email": stakeholder.email,
        "phone": stakeholder.phone,
        "engagement_level": stakeholder.engagement_level,
        "influence_level": stakeholder.influence_level,
        "notes": stakeholder.notes,
        "created_at": stakeholder.created_at.isoformat() if stakeholder.created_at else None
    }
