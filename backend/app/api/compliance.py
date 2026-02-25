"""
Compliance Dashboard API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas
from typing import List

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])


@router.get("/metrics", response_model=schemas.ComplianceMetricsResponse)
def get_compliance_metrics(db: Session = Depends(get_db)):
    """
    Get real-time compliance metrics for dashboard.
    """
    total = db.query(func.count(models.Asset.asset_id)).scalar()
    compliant = db.query(func.count(models.Asset.asset_id)).filter(
        models.Asset.naming_compliant == True
    ).scalar()

    compliance_rate = round((compliant / total * 100), 2) if total > 0 else 0
    non_compliant = total - compliant

    missing_docs = db.query(func.count(models.Asset.asset_id)).filter(
        (models.Asset.documentation_url == None) | (models.Asset.documentation_url == ""),
        models.Asset.lifecycle_stage == "Active"
    ).scalar()

    pending_changes = db.query(func.count(models.ChangeRequest.change_id)).filter(
        models.ChangeRequest.approval_status == "Pending"
    ).scalar()

    return {
        "total_assets": total,
        "compliant_assets": compliant,
        "compliance_rate": compliance_rate,
        "non_compliant_assets": non_compliant,
        "missing_documentation": missing_docs,
        "pending_changes": pending_changes
    }


@router.get("/violations")
def get_violations(db: Session = Depends(get_db)):
    """Get all unresolved compliance violations"""
    violations = db.query(models.ComplianceViolation).filter(
        models.ComplianceViolation.resolved_at == None
    ).all()

    return {"violations": [
        {
            "violation_id": v.violation_id,
            "asset_id": v.asset_id,
            "violation_type": v.violation_type,
            "severity": v.severity,
            "description": v.description,
            "detected_at": v.detected_at
        }
        for v in violations
    ]}


@router.post("/validate/naming", response_model=schemas.NamingValidationResponse)
def validate_naming(request: schemas.NamingValidationRequest, db: Session = Depends(get_db)):
    """Validate asset name against naming convention"""
    from ..services.naming_validator import NamingValidator

    is_valid, violations = NamingValidator.validate(request.asset_name, db)
    suggestions = NamingValidator.suggest_corrections(request.asset_name, db) if not is_valid else []

    return {
        "valid": is_valid,
        "violations": violations,
        "suggestions": suggestions
    }


@router.get("/domains", response_model=List[schemas.DomainResponse])
def get_approved_domains(db: Session = Depends(get_db)):
    """Get list of approved business domains"""
    domains = db.query(models.Domain).filter(models.Domain.is_active == True).all()
    return domains
