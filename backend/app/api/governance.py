"""
Governance API
Endpoints for governance policies and compliance rules
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models_advanced import GovernancePolicy

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


@router.get("/policies", response_model=List[dict])
def get_governance_policies(
    active_only: bool = Query(True, description="Show only active policies"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    enforcement_level: Optional[str] = Query(None, description="Filter by enforcement level"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get governance policies

    Returns governance policy rules including:
    - Policy name and type
    - Enforcement level (advisory, warning, blocking)
    - Policy definition (JSON rules)
    - Applicability (domains, environments)
    - Exemption settings

    No authentication required for read access.
    """
    query = db.query(GovernancePolicy)

    if active_only:
        query = query.filter(GovernancePolicy.is_active == True)

    if policy_type:
        query = query.filter(GovernancePolicy.policy_type == policy_type)

    if enforcement_level:
        query = query.filter(GovernancePolicy.enforcement_level == enforcement_level)

    policies = query.offset(skip).limit(limit).all()

    return [
        {
            "policy_id": p.policy_id,
            "policy_name": p.policy_name,
            "policy_type": p.policy_type.value if hasattr(p.policy_type, 'value') else str(p.policy_type),
            "description": p.description,
            "policy_definition": p.policy_definition,
            "is_active": p.is_active,
            "is_blocking": p.is_blocking,
            "enforcement_level": p.enforcement_level,
            "applies_to_domains": p.applies_to_domains,
            "applies_to_environments": p.applies_to_environments,
            "exemption_allowed": p.exemption_allowed,
            "exemption_requires_approval": p.exemption_requires_approval,
            "created_by": p.created_by,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        }
        for p in policies
    ]
