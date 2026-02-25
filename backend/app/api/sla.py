"""
SLA Monitoring API Endpoints
Provides real-time SLA tracking, metric collection, and violation management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from ..services.sla_monitor import SLAMonitor
from ..database import get_db

router = APIRouter(prefix="/api/v1/sla", tags=["SLA Monitoring"])


class SLAMetricDefine(BaseModel):
    metric_name: str
    metric_type: str  # AVAILABILITY, PERFORMANCE, RELIABILITY, FRESHNESS, CAPACITY
    target_value: float
    target_unit: str
    vendor_id: Optional[int] = None
    asset_id: Optional[int] = None
    metric_source: str = "manual"
    collection_method: str = "api"
    description: Optional[str] = None


class MetricCollection(BaseModel):
    current_value: float
    timestamp: Optional[datetime] = None


class PrometheusCollection(BaseModel):
    prometheus_url: str
    query: str


class CloudWatchCollection(BaseModel):
    aws_region: str
    namespace: str
    metric_name: str
    dimensions: Dict
    statistic: str = "Average"
    period_minutes: int = 5


@router.post("/metrics/define")
def define_sla_metric(
    request: SLAMetricDefine,
    db: Session = Depends(get_db)
):
    """
    Define a new SLA metric to monitor

    Args:
        request: SLA metric definition

    Returns:
        Created metric information

    Example:
        {
          "metric_name": "API Response Time",
          "metric_type": "PERFORMANCE",
          "target_value": 200.0,
          "target_unit": "milliseconds",
          "asset_id": 1,
          "metric_source": "prometheus"
        }
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.define_sla_metric(
            metric_name=request.metric_name,
            metric_type=request.metric_type,
            target_value=request.target_value,
            target_unit=request.target_unit,
            vendor_id=request.vendor_id,
            asset_id=request.asset_id,
            metric_source=request.metric_source,
            collection_method=request.collection_method,
            description=request.description
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SLA metric creation failed: {str(e)}")


@router.post("/metrics/{metric_id}/collect")
def collect_metric_value(
    metric_id: int,
    request: MetricCollection,
    db: Session = Depends(get_db)
):
    """
    Record a new metric measurement

    Args:
        metric_id: Metric to update
        request: Current value and optional timestamp

    Returns:
        Metric status with breach detection

    Example:
        {
          "current_value": 175.5,
          "timestamp": "2026-02-22T10:30:00Z"
        }
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.collect_metric(
            metric_id=metric_id,
            current_value=request.current_value,
            timestamp=request.timestamp
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metric collection failed: {str(e)}")


@router.post("/metrics/{metric_id}/collect/prometheus")
def collect_from_prometheus(
    metric_id: int,
    request: PrometheusCollection,
    db: Session = Depends(get_db)
):
    """
    Collect metric from Prometheus using PromQL

    Args:
        metric_id: Metric to update
        request: Prometheus connection and query

    Returns:
        Collection result with SLA status

    Example:
        {
          "prometheus_url": "http://prometheus:9090",
          "query": "avg(http_request_duration_seconds{job='api'})"
        }
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.collect_from_prometheus(
            metric_id=metric_id,
            prometheus_url=request.prometheus_url,
            query=request.query
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prometheus collection failed: {str(e)}")


@router.post("/metrics/{metric_id}/collect/cloudwatch")
def collect_from_cloudwatch(
    metric_id: int,
    request: CloudWatchCollection,
    db: Session = Depends(get_db)
):
    """
    Collect metric from AWS CloudWatch

    Args:
        metric_id: Metric to update
        request: CloudWatch connection parameters

    Returns:
        Collection result with SLA status

    Example:
        {
          "aws_region": "us-east-1",
          "namespace": "AWS/RDS",
          "metric_name": "DatabaseConnections",
          "dimensions": {"DBInstanceIdentifier": "mydb"},
          "statistic": "Average",
          "period_minutes": 5
        }
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.collect_from_cloudwatch(
            metric_id=metric_id,
            aws_region=request.aws_region,
            namespace=request.namespace,
            metric_name=request.metric_name,
            dimensions=request.dimensions,
            statistic=request.statistic,
            period_minutes=request.period_minutes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CloudWatch collection failed: {str(e)}")


@router.get("/status")
def get_sla_status(
    vendor_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get current SLA status for vendor or asset

    Args:
        vendor_id: Filter by vendor (optional)
        asset_id: Filter by asset (optional)

    Returns:
        Current SLA metrics and compliance status

    Example:
        GET /api/v1/sla/status?asset_id=1
    """
    if not vendor_id and not asset_id:
        raise HTTPException(status_code=400, detail="Either vendor_id or asset_id must be specified")

    try:
        monitor = SLAMonitor(db)
        result = monitor.get_sla_status(
            vendor_id=vendor_id,
            asset_id=asset_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SLA status: {str(e)}")


@router.get("/violations")
def get_violations(
    metric_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    resolved: Optional[bool] = None,
    lookback_days: int = 30,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get SLA violations with filters

    Args:
        metric_id: Filter by specific metric
        vendor_id: Filter by vendor
        asset_id: Filter by asset
        resolved: Filter by resolution status (true/false/null for all)
        lookback_days: Days to look back (default 30)
        limit: Maximum violations to return (default 100)

    Returns:
        List of violation records

    Example:
        GET /api/v1/sla/violations?asset_id=1&resolved=false&lookback_days=7
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.get_violations(
            metric_id=metric_id,
            vendor_id=vendor_id,
            asset_id=asset_id,
            resolved=resolved,
            lookback_days=lookback_days,
            limit=limit
        )
        return {
            "total": len(result),
            "violations": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get violations: {str(e)}")


@router.get("/metrics/{metric_id}/trend")
def get_compliance_trend(
    metric_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get SLA compliance trend and statistics over time

    Args:
        metric_id: Metric to analyze
        days: Days to analyze (default 30)

    Returns:
        Compliance trend with MTTR and violation breakdown

    Example:
        GET /api/v1/sla/metrics/1/trend?days=90
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.get_compliance_trend(
            metric_id=metric_id,
            days=days
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate trend: {str(e)}")


@router.get("/metrics")
def list_sla_metrics(
    vendor_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    metric_type: Optional[str] = None,
    compliant_only: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List SLA metrics with optional filters

    Args:
        vendor_id: Filter by vendor
        asset_id: Filter by asset
        metric_type: Filter by metric type
        compliant_only: Only return compliant metrics
        limit: Maximum metrics to return
        offset: Offset for pagination

    Returns:
        List of SLA metrics with current status
    """
    from .. import models_advanced
    from sqlalchemy import and_

    query = db.query(models_advanced.SLAMonitoring)

    filters = []
    if vendor_id:
        filters.append(models_advanced.SLAMonitoring.vendor_id == vendor_id)
    if asset_id:
        filters.append(models_advanced.SLAMonitoring.asset_id == asset_id)
    if metric_type:
        filters.append(models_advanced.SLAMonitoring.metric_type == models_advanced.SLAMetricType[metric_type])
    if compliant_only is not None:
        filters.append(models_advanced.SLAMonitoring.is_within_sla == compliant_only)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    metrics = query.limit(limit).offset(offset).all()

    return {
        "total": total,
        "count": len(metrics),
        "metrics": [{
            "metric_id": m.metric_id,
            "metric_name": m.metric_name,
            "metric_type": m.metric_type.value,
            "vendor_id": m.vendor_id,
            "asset_id": m.asset_id,
            "target_value": m.target_value,
            "target_unit": m.target_unit,
            "current_value": m.current_value,
            "is_within_sla": m.is_within_sla,
            "deviation_percentage": round(m.deviation_percentage, 2) if m.deviation_percentage else None,
            "metric_source": m.metric_source,
            "last_measured": m.measurement_timestamp.isoformat() if m.measurement_timestamp else None
        } for m in metrics]
    }


@router.get("/statistics")
def get_sla_statistics(db: Session = Depends(get_db)):
    """
    Get overall SLA monitoring statistics

    Returns:
        System-wide SLA statistics and compliance rates
    """
    try:
        monitor = SLAMonitor(db)
        result = monitor.get_sla_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.patch("/metrics/{metric_id}")
def update_sla_metric(
    metric_id: int,
    target_value: Optional[float] = None,
    metric_source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update SLA metric configuration

    Args:
        metric_id: Metric to update
        target_value: New target value
        metric_source: New metric source

    Returns:
        Updated metric information
    """
    from .. import models_advanced

    metric = db.query(models_advanced.SLAMonitoring).filter(
        models_advanced.SLAMonitoring.metric_id == metric_id
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {metric_id} not found")

    if target_value is not None:
        metric.target_value = target_value
    if metric_source is not None:
        metric.metric_source = metric_source

    db.commit()

    return {
        "metric_id": metric_id,
        "metric_name": metric.metric_name,
        "target_value": metric.target_value,
        "metric_source": metric.metric_source,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.delete("/metrics/{metric_id}")
def delete_sla_metric(
    metric_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an SLA metric

    Args:
        metric_id: Metric to delete

    Returns:
        Deletion confirmation
    """
    from .. import models_advanced

    metric = db.query(models_advanced.SLAMonitoring).filter(
        models_advanced.SLAMonitoring.metric_id == metric_id
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {metric_id} not found")

    metric_name = metric.metric_name
    db.delete(metric)
    db.commit()

    return {
        "metric_id": metric_id,
        "metric_name": metric_name,
        "deleted_at": datetime.utcnow().isoformat()
    }


@router.patch("/violations/{violation_id}/resolve")
def resolve_violation(
    violation_id: int,
    root_cause: Optional[str] = None,
    remediation_actions: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Manually resolve an SLA violation

    Args:
        violation_id: Violation to resolve
        root_cause: Root cause description
        remediation_actions: Actions taken

    Returns:
        Updated violation information
    """
    from .. import models_advanced

    violation = db.query(models_advanced.SLAViolation).filter(
        models_advanced.SLAViolation.violation_id == violation_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

    if violation.resolved_at:
        raise HTTPException(status_code=400, detail="Violation already resolved")

    violation.resolved_at = datetime.utcnow()
    violation.duration_minutes = int((violation.resolved_at - violation.violated_at).total_seconds() / 60)

    if root_cause:
        violation.root_cause = root_cause
    if remediation_actions:
        violation.remediation_actions = remediation_actions

    db.commit()

    return {
        "violation_id": violation_id,
        "resolved_at": violation.resolved_at.isoformat(),
        "duration_minutes": violation.duration_minutes,
        "root_cause": violation.root_cause,
        "remediation_actions": violation.remediation_actions
    }
