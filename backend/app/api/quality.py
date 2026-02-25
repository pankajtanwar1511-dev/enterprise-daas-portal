"""
Data Quality API Endpoints
Provides quality rule management, execution, and scoring capabilities
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..services.quality_engine import QualityEngine
from ..database import get_db

router = APIRouter(prefix="/api/v1/quality", tags=["Data Quality"])


class QualityRuleCreate(BaseModel):
    rule_name: str
    asset_id: int
    quality_dimension: str  # COMPLETENESS, ACCURACY, CONSISTENCY, TIMELINESS, VALIDITY, UNIQUENESS
    rule_type: str  # sql, regex, python, great_expectations
    rule_definition: str
    threshold_value: Optional[float] = None
    threshold_operator: str = "<="
    severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    is_active: bool = True
    schedule: str = "daily"
    alert_channels: Optional[List[str]] = None
    description: Optional[str] = None


class RuleFromTemplate(BaseModel):
    template_name: str
    asset_id: int
    rule_name: str
    parameters: Dict
    threshold_value: Optional[float] = None
    severity: str = "MEDIUM"


@router.post("/rules")
def create_quality_rule(
    request: QualityRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new data quality rule

    Args:
        request: Quality rule definition

    Returns:
        Created rule information
    """
    try:
        engine = QualityEngine(db)
        result = engine.create_rule(
            rule_name=request.rule_name,
            asset_id=request.asset_id,
            quality_dimension=request.quality_dimension,
            rule_type=request.rule_type,
            rule_definition=request.rule_definition,
            threshold_value=request.threshold_value,
            threshold_operator=request.threshold_operator,
            severity=request.severity,
            is_active=request.is_active,
            schedule=request.schedule,
            alert_channels=request.alert_channels,
            description=request.description
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rule creation failed: {str(e)}")


@router.post("/rules/from-template")
def create_rule_from_template(
    request: RuleFromTemplate,
    db: Session = Depends(get_db)
):
    """
    Create quality rule from pre-built template

    Args:
        request: Template name and parameters

    Returns:
        Created rule information

    Available templates:
    - null_check: Check for null values
    - unique_check: Check for duplicates
    - range_check: Check value ranges
    - format_check: Check format patterns
    - freshness_check: Check data freshness
    - referential_integrity: Check foreign key relationships
    """
    try:
        engine = QualityEngine(db)
        result = engine.create_rule_from_template(
            template_name=request.template_name,
            asset_id=request.asset_id,
            rule_name=request.rule_name,
            parameters=request.parameters,
            threshold_value=request.threshold_value,
            severity=request.severity
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rule creation from template failed: {str(e)}")


@router.get("/rules/templates")
def list_rule_templates():
    """
    List available rule templates with descriptions

    Returns:
        Dict of available templates with metadata
    """
    return {
        "templates": QualityEngine.RULE_TEMPLATES,
        "count": len(QualityEngine.RULE_TEMPLATES)
    }


@router.post("/rules/{rule_id}/execute")
def execute_quality_rule(
    rule_id: int,
    sample_size: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Execute a quality rule and record results

    Args:
        rule_id: Rule to execute
        sample_size: Optional row limit for sampling

    Returns:
        Execution results with pass/fail status
    """
    try:
        engine = QualityEngine(db)
        result = engine.execute_rule(
            rule_id=rule_id,
            sample_size=sample_size
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rule execution failed: {str(e)}")


@router.post("/assets/{asset_id}/execute-rules")
def execute_all_rules_for_asset(
    asset_id: int,
    dimension: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Execute all quality rules for an asset

    Args:
        asset_id: Asset to validate
        dimension: Optional dimension filter

    Returns:
        Execution summary with pass/fail statistics
    """
    try:
        engine = QualityEngine(db)
        result = engine.execute_rules_for_asset(
            asset_id=asset_id,
            dimension=dimension
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk rule execution failed: {str(e)}")


@router.get("/assets/{asset_id}/score")
def get_quality_score(
    asset_id: int,
    lookback_days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Calculate overall quality score for an asset

    Args:
        asset_id: Asset to score
        lookback_days: Days to consider for scoring

    Returns:
        Quality score breakdown by dimension with letter grade
    """
    try:
        engine = QualityEngine(db)
        result = engine.get_quality_score(
            asset_id=asset_id,
            lookback_days=lookback_days
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality score calculation failed: {str(e)}")


@router.get("/rules/{rule_id}/history")
def get_rule_execution_history(
    rule_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get execution history for a rule

    Args:
        rule_id: Rule ID
        limit: Maximum number of runs to return

    Returns:
        List of historical check runs with results
    """
    try:
        engine = QualityEngine(db)
        result = engine.get_rule_history(
            rule_id=rule_id,
            limit=limit
        )
        return {"rule_id": rule_id, "history": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/rules/{rule_id}/anomalies")
def detect_rule_anomalies(
    rule_id: int,
    lookback_runs: int = 30,
    std_dev_threshold: float = 2.0,
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in rule execution results using statistical analysis

    Args:
        rule_id: Rule to analyze
        lookback_runs: Number of historical runs to consider
        std_dev_threshold: Number of standard deviations for anomaly

    Returns:
        Anomaly detection results with z-score analysis
    """
    try:
        engine = QualityEngine(db)
        result = engine.detect_anomalies(
            rule_id=rule_id,
            lookback_runs=lookback_runs,
            std_dev_threshold=std_dev_threshold
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.get("/rules")
def list_quality_rules(
    asset_id: Optional[int] = None,
    dimension: Optional[str] = None,
    enabled_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List quality rules with optional filters

    Args:
        asset_id: Filter by asset
        dimension: Filter by quality dimension
        enabled_only: Only return enabled rules
        limit: Maximum number of rules to return
        offset: Offset for pagination

    Returns:
        List of quality rules with metadata
    """
    from .. import models_advanced
    from sqlalchemy import and_

    query = db.query(models_advanced.DataQualityRule)

    filters = []
    if asset_id:
        filters.append(models_advanced.DataQualityRule.asset_id == asset_id)
    if dimension:
        filters.append(models_advanced.DataQualityRule.quality_dimension == models_advanced.QualityDimension[dimension])
    if enabled_only:
        filters.append(models_advanced.DataQualityRule.is_active == True)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    rules = query.limit(limit).offset(offset).all()

    return {
        "total": total,
        "count": len(rules),
        "rules": [{
            "rule_id": r.rule_id,
            "rule_name": r.rule_name,
            "asset_id": r.asset_id,
            "quality_dimension": r.quality_dimension.value,
            "rule_type": r.rule_type,
            "severity": r.severity.value,
            "is_active": r.is_active,
            "threshold_value": r.threshold_value,
            "threshold_operator": r.threshold_operator,
            "last_run": r.last_run.isoformat() if r.last_run else None,
            "created_at": r.created_at.isoformat()
        } for r in rules]
    }


@router.get("/statistics")
def get_quality_statistics(db: Session = Depends(get_db)):
    """
    Get data quality statistics across the system

    Returns:
        Overall quality statistics and trends
    """
    from .. import models_advanced
    from sqlalchemy import func

    total_rules = db.query(models_advanced.DataQualityRule).count()
    enabled_rules = db.query(models_advanced.DataQualityRule).filter(
        models_advanced.DataQualityRule.is_active == True
    ).count()

    # Count by dimension
    dimension_counts = db.query(
        models_advanced.DataQualityRule.quality_dimension,
        func.count(models_advanced.DataQualityRule.rule_id)
    ).group_by(
        models_advanced.DataQualityRule.quality_dimension
    ).all()

    # Count by severity
    severity_counts = db.query(
        models_advanced.DataQualityRule.severity,
        func.count(models_advanced.DataQualityRule.rule_id)
    ).group_by(
        models_advanced.DataQualityRule.severity
    ).all()

    # Recent check runs
    total_check_runs = db.query(models_advanced.QualityCheckRun).count()
    passed_runs = db.query(models_advanced.QualityCheckRun).filter(
        models_advanced.QualityCheckRun.passed == True
    ).count()

    return {
        "total_rules": total_rules,
        "enabled_rules": enabled_rules,
        "disabled_rules": total_rules - enabled_rules,
        "rules_by_dimension": {
            dim.value: count for dim, count in dimension_counts
        },
        "rules_by_severity": {
            sev.value: count for sev, count in severity_counts
        },
        "total_check_runs": total_check_runs,
        "overall_pass_rate": round(passed_runs / total_check_runs * 100, 2) if total_check_runs > 0 else None
    }


@router.patch("/rules/{rule_id}")
def update_quality_rule(
    rule_id: int,
    is_active: Optional[bool] = None,
    threshold_value: Optional[float] = None,
    severity: Optional[str] = None,
    alert_channels: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Update quality rule configuration

    Args:
        rule_id: Rule to update
        is_active: Enable/disable rule
        threshold_value: New threshold value
        severity: New severity level
        alert_channels: New alert channels

    Returns:
        Updated rule information
    """
    from .. import models_advanced

    rule = db.query(models_advanced.DataQualityRule).filter(
        models_advanced.DataQualityRule.rule_id == rule_id
    ).first()

    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    if is_active is not None:
        rule.is_active = is_active
    if threshold_value is not None:
        rule.threshold_value = threshold_value
    if severity is not None:
        rule.severity = models_advanced.QualityRuleSeverity[severity]
    if alert_channels is not None:
        rule.alert_channels = alert_channels

    db.commit()

    return {
        "rule_id": rule_id,
        "rule_name": rule.rule_name,
        "is_active": rule.is_active,
        "threshold_value": rule.threshold_value,
        "severity": rule.severity.value,
        "alert_channels": rule.alert_channels,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.delete("/rules/{rule_id}")
def delete_quality_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a quality rule

    Args:
        rule_id: Rule to delete

    Returns:
        Deletion confirmation
    """
    from .. import models_advanced

    rule = db.query(models_advanced.DataQualityRule).filter(
        models_advanced.DataQualityRule.rule_id == rule_id
    ).first()

    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    rule_name = rule.rule_name
    db.delete(rule)
    db.commit()

    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "deleted_at": datetime.utcnow().isoformat()
    }


from datetime import datetime
