"""
Asset Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..services.naming_validator import NamingValidator
from ..dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])


@router.post("/", response_model=schemas.AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new asset with naming validation"""

    # Validate naming convention
    is_valid, violations = NamingValidator.validate(asset.asset_name, db)

    # Create asset (store compliance status)
    new_asset = models.Asset(
        **asset.model_dump(),
        naming_compliant=is_valid,
        compliance_check_date=datetime.utcnow(),
        created_by=current_user.user_id
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    # Create compliance violations if not compliant
    if not is_valid:
        for violation_desc in violations:
            violation = models.ComplianceViolation(
                asset_id=new_asset.asset_id,
                violation_type="Naming",
                severity="High",
                description=violation_desc
            )
            db.add(violation)
        db.commit()

    return new_asset


@router.get("/", response_model=List[schemas.AssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    environment: str = None,
    lifecycle_stage: str = None,
    compliant: bool = None,
    db: Session = Depends(get_db)
):
    """List all assets with optional filters"""
    query = db.query(models.Asset)

    if environment:
        query = query.filter(models.Asset.environment == environment)
    if lifecycle_stage:
        query = query.filter(models.Asset.lifecycle_stage == lifecycle_stage)
    if compliant is not None:
        query = query.filter(models.Asset.naming_compliant == compliant)

    assets = query.offset(skip).limit(limit).all()
    return assets


@router.get("/domains", response_model=List[schemas.DomainResponse])
def get_domains(db: Session = Depends(get_db)):
    """Get all active domains for dropdown"""
    domains = db.query(models.Domain).filter(models.Domain.is_active == True).all()
    return domains


@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all active users for dropdown"""
    users = db.query(models.User).filter(models.User.is_active == True).all()
    return users


@router.post("/validate-naming")
def validate_naming(request: schemas.NamingValidationRequest, db: Session = Depends(get_db)):
    """Validate asset name against naming convention"""
    # Support excluding an asset ID for update validation
    exclude_id = getattr(request, 'exclude_asset_id', None)
    is_valid, violations = NamingValidator.validate(request.asset_name, db, exclude_asset_id=exclude_id)

    # Return response matching frontend expectations
    return {
        "is_valid": is_valid,
        "valid": is_valid,  # Also include for compatibility
        "violations": violations,
        "expected_format": "ENV-DOMAIN-SYSTEM-VERSION (e.g., PROD-HR-DW-v1)" if not is_valid else None
    }


@router.get("/count")
def get_assets_count(
    environment: str = None,
    lifecycle_stage: str = None,
    compliant: bool = None,
    db: Session = Depends(get_db)
):
    """Get total count of assets with optional filters"""
    from sqlalchemy import func

    query = db.query(func.count(models.Asset.asset_id))

    if environment:
        query = query.filter(models.Asset.environment == environment)
    if lifecycle_stage:
        query = query.filter(models.Asset.lifecycle_stage == lifecycle_stage)
    if compliant is not None:
        query = query.filter(models.Asset.naming_compliant == compliant)

    count = query.scalar()
    return {"count": count}


@router.get("/{asset_id}", response_model=schemas.AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset by ID"""
    asset = db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/{asset_id}/lifecycle-history", response_model=List[schemas.LifecycleHistoryResponse])
def get_lifecycle_history(asset_id: int, db: Session = Depends(get_db)):
    """Get lifecycle history for an asset"""
    # Verify asset exists
    asset = db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Get lifecycle history ordered by most recent first
    history = (
        db.query(models.LifecycleHistory)
        .filter(models.LifecycleHistory.asset_id == asset_id)
        .order_by(models.LifecycleHistory.changed_at.desc())
        .all()
    )

    return history


@router.put("/{asset_id}", response_model=schemas.AssetResponse)
def update_asset(asset_id: int, asset_update: schemas.AssetUpdate, db: Session = Depends(get_db)):
    """Update asset"""
    asset = db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update fields
    update_data = asset_update.model_dump(exclude_unset=True)

    # Re-validate if name changed
    if "asset_name" in update_data:
        is_valid, violations = NamingValidator.validate(
            update_data["asset_name"],
            db,
            exclude_asset_id=asset_id  # Exclude current asset from duplicate check
        )
        update_data["naming_compliant"] = is_valid
        update_data["compliance_check_date"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(asset, field, value)

    asset.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete asset"""
    asset = db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()
    return None
