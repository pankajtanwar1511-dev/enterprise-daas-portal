"""
Policy Enforcement API Endpoints
Provides CI/CD integration for automated governance policy validation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..services.policy_enforcer import PolicyEnforcer
from ..database import get_db

router = APIRouter(prefix="/api/v1/policies", tags=["Policy Enforcement"])


class PolicyCreate(BaseModel):
    policy_name: str
    policy_type: str  # NAMING_CONVENTION, DOCUMENTATION, DATA_CLASSIFICATION, OWNER_ASSIGNMENT
    policy_definition: Dict
    is_blocking: bool = True
    enforcement_level: str = "strict"
    applies_to_domains: Optional[List[str]] = None
    applies_to_environments: Optional[List[str]] = None
    description: Optional[str] = None


class AssetValidation(BaseModel):
    asset_name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    environment: Optional[str] = None
    domain: Optional[str] = None
    data_classification: Optional[str] = None
    business_purpose: Optional[str] = None
    encryption_required: Optional[bool] = None
    access_control_policy: Optional[str] = None
    pipeline_context: Optional[Dict] = None


class NamingValidation(BaseModel):
    asset_name: str
    expected_pattern: Optional[str] = None


@router.post("/create")
def create_governance_policy(
    request: PolicyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new governance policy

    Args:
        request: Policy definition

    Returns:
        Created policy information
    """
    try:
        enforcer = PolicyEnforcer(db)
        result = enforcer.create_policy(
            policy_name=request.policy_name,
            policy_type=request.policy_type,
            policy_definition=request.policy_definition,
            is_blocking=request.is_blocking,
            enforcement_level=request.enforcement_level,
            applies_to_domains=request.applies_to_domains,
            applies_to_environments=request.applies_to_environments,
            description=request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy creation failed: {str(e)}")


@router.post("/validate")
def validate_asset_policies(
    request: AssetValidation,
    db: Session = Depends(get_db)
):
    """
    Validate asset data against all applicable governance policies

    This endpoint is designed to be called from CI/CD pipelines
    to validate that assets meet governance requirements before deployment.

    Args:
        request: Asset metadata to validate

    Returns:
        Validation result with violations and warnings
    """
    try:
        enforcer = PolicyEnforcer(db)

        asset_data = {
            "asset_name": request.asset_name,
            "description": request.description,
            "owner_id": request.owner_id,
            "environment": request.environment,
            "domain": request.domain,
            "data_classification": request.data_classification,
            "business_purpose": request.business_purpose,
            "encryption_required": request.encryption_required,
            "access_control_policy": request.access_control_policy
        }

        result = enforcer.validate_asset(
            asset_data=asset_data,
            pipeline_context=request.pipeline_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/validate/naming")
def validate_naming_convention(
    request: NamingValidation,
    db: Session = Depends(get_db)
):
    """
    Validate asset naming against standard convention

    Default pattern: {ENV}-{DOMAIN}-{SYSTEM}-{VERSION}
    Example: PROD-SALES-CUSTOMER-v1

    Args:
        request: Asset name and optional custom pattern

    Returns:
        Validation result with parsed components
    """
    try:
        enforcer = PolicyEnforcer(db)
        result = enforcer.validate_naming_convention(
            asset_name=request.asset_name,
            expected_pattern=request.expected_pattern
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Naming validation failed: {str(e)}")


@router.get("/integrations/github-actions")
def get_github_actions_config(
    asset_name_var: str = "${{ env.ASSET_NAME }}"
):
    """
    Generate GitHub Actions workflow configuration for policy validation

    Args:
        asset_name_var: GitHub Actions variable for asset name

    Returns:
        YAML configuration string for GitHub Actions workflow
    """
    from ..services.policy_enforcer import PolicyEnforcer
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        enforcer = PolicyEnforcer(db)
        config = enforcer.generate_github_action_config(asset_name_var)
        return {
            "platform": "GitHub Actions",
            "config": config,
            "instructions": [
                "1. Copy the YAML configuration below",
                "2. Save as .github/workflows/governance-check.yml",
                "3. Set secrets: GOVERNANCE_PORTAL_URL and GOVERNANCE_API_TOKEN",
                "4. Push to your repository"
            ]
        }
    finally:
        db.close()


@router.get("/integrations/gitlab-ci")
def get_gitlab_ci_config():
    """
    Generate GitLab CI configuration for policy validation

    Returns:
        YAML configuration string for GitLab CI
    """
    from ..services.policy_enforcer import PolicyEnforcer
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        enforcer = PolicyEnforcer(db)
        config = enforcer.generate_gitlab_ci_config()
        return {
            "platform": "GitLab CI",
            "config": config,
            "instructions": [
                "1. Copy the YAML configuration below",
                "2. Add to your .gitlab-ci.yml file",
                "3. Set CI/CD variables: GOVERNANCE_PORTAL_URL and GOVERNANCE_API_TOKEN",
                "4. Push to your repository"
            ]
        }
    finally:
        db.close()


@router.get("/list")
def list_policies(
    enabled_only: bool = False,
    policy_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all governance policies with optional filters

    Args:
        enabled_only: Only return enabled policies
        policy_type: Filter by policy type
        limit: Maximum number of policies to return
        offset: Offset for pagination

    Returns:
        List of policies with metadata
    """
    from .. import models_advanced
    from sqlalchemy import and_

    query = db.query(models_advanced.GovernancePolicy)

    filters = []
    if enabled_only:
        filters.append(models_advanced.GovernancePolicy.is_active == True)
    if policy_type:
        filters.append(models_advanced.GovernancePolicy.policy_type == models_advanced.PolicyType[policy_type])

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    policies = query.limit(limit).offset(offset).all()

    return {
        "total": total,
        "count": len(policies),
        "policies": [{
            "policy_id": p.policy_id,
            "policy_name": p.policy_name,
            "policy_type": p.policy_type.value,
            "is_blocking": p.is_blocking,
            "is_active": p.is_active,
            "enforcement_level": p.enforcement_level,
            "applies_to_domains": p.applies_to_domains,
            "applies_to_environments": p.applies_to_environments,
            "created_at": p.created_at.isoformat()
        } for p in policies]
    }


@router.get("/validations")
def list_validation_history(
    limit: int = 50,
    offset: int = 0,
    passed_only: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List recent policy validation runs

    Args:
        limit: Maximum number of validations to return
        offset: Offset for pagination
        passed_only: Filter by passed status

    Returns:
        List of validation results
    """
    from .. import models_advanced

    query = db.query(models_advanced.PolicyValidation)

    if passed_only is not None:
        query = query.filter(models_advanced.PolicyValidation.passed == passed_only)

    query = query.order_by(models_advanced.PolicyValidation.validated_at.desc())

    total = query.count()
    validations = query.limit(limit).offset(offset).all()

    return {
        "total": total,
        "count": len(validations),
        "validations": [{
            "validation_id": v.validation_id,
            "asset_name": v.asset_name,
            "passed": v.passed,
            "violation_count": len(v.violations) if v.violations else 0,
            "validated_at": v.validated_at.isoformat()
        } for v in validations]
    }


@router.get("/statistics")
def get_policy_statistics(db: Session = Depends(get_db)):
    """
    Get policy enforcement statistics

    Returns:
        Overall policy enforcement statistics
    """
    try:
        enforcer = PolicyEnforcer(db)
        result = enforcer.get_policy_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.patch("/policies/{policy_id}")
def update_policy(
    policy_id: int,
    is_active: Optional[bool] = None,
    is_blocking: Optional[bool] = None,
    enforcement_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update policy configuration

    Args:
        policy_id: Policy to update
        is_active: Enable/disable policy
        is_blocking: Make blocking/non-blocking
        enforcement_level: New enforcement level

    Returns:
        Updated policy information
    """
    from .. import models_advanced

    policy = db.query(models_advanced.GovernancePolicy).filter(
        models_advanced.GovernancePolicy.policy_id == policy_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")

    if is_active is not None:
        policy.is_active = is_active
    if is_blocking is not None:
        policy.is_blocking = is_blocking
    if enforcement_level is not None:
        policy.enforcement_level = enforcement_level

    db.commit()

    return {
        "policy_id": policy_id,
        "policy_name": policy.policy_name,
        "is_active": policy.is_active,
        "is_blocking": policy.is_blocking,
        "enforcement_level": policy.enforcement_level
    }


@router.delete("/policies/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a governance policy

    Args:
        policy_id: Policy to delete

    Returns:
        Deletion confirmation
    """
    from .. import models_advanced

    policy = db.query(models_advanced.GovernancePolicy).filter(
        models_advanced.GovernancePolicy.policy_id == policy_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")

    policy_name = policy.policy_name
    db.delete(policy)
    db.commit()

    return {
        "policy_id": policy_id,
        "policy_name": policy_name,
        "deleted_at": datetime.utcnow().isoformat()
    }


from datetime import datetime
