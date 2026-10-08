"""
SLA Monitoring and Real-Time Metric Collection
Integrates with Prometheus, CloudWatch, Datadog for real-time SLA tracking
Detects breaches, calculates compliance scores, and triggers alerts
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from .. import models, models_advanced
import statistics


class SLAMonitor:
    """
    Real-time SLA monitoring and metric collection
    Supports integration with external monitoring platforms
    """

    def __init__(self, db: Session):
        self.db = db

    def define_sla_metric(
        self,
        metric_name: str,
        metric_type: str,
        target_value: float,
        target_unit: str,
        vendor_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        metric_source: str = "manual",
        collection_method: str = "api",
        description: Optional[str] = None
    ) -> Dict:
        """
        Define a new SLA metric to monitor

        Args:
            metric_name: Name of the metric (e.g., "API Response Time")
            metric_type: Type from SLAMetricType enum
            target_value: Target SLA value (e.g., 99.9 for availability)
            target_unit: Unit of measurement (percent, milliseconds, etc.)
            vendor_id: Vendor this SLA applies to
            asset_id: Asset this SLA applies to
            metric_source: prometheus, cloudwatch, datadog, manual
            collection_method: api, agent, webhook
            description: Description of the metric

        Returns:
            Dict with created metric information
        """
        # Validate that at least vendor or asset is specified
        if not vendor_id and not asset_id:
            raise ValueError("Either vendor_id or asset_id must be specified")

        # Validate asset/vendor exists
        if asset_id:
            asset = self.db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")

        if vendor_id:
            vendor = self.db.query(models.Vendor).filter(models.Vendor.vendor_id == vendor_id).first()
            if not vendor:
                raise ValueError(f"Vendor {vendor_id} not found")

        # Create initial metric with no current value
        metric = models_advanced.SLAMonitoring(
            vendor_id=vendor_id,
            asset_id=asset_id,
            metric_type=models_advanced.SLAMetricType[metric_type],
            metric_name=metric_name,
            target_value=target_value,
            target_unit=target_unit,
            measurement_timestamp=datetime.utcnow(),
            metric_source=metric_source,
            collection_method=collection_method,
            created_at=datetime.utcnow()
        )

        self.db.add(metric)
        self.db.commit()

        return {
            "metric_id": metric.metric_id,
            "metric_name": metric_name,
            "metric_type": metric_type,
            "target_value": target_value,
            "target_unit": target_unit,
            "vendor_id": vendor_id,
            "asset_id": asset_id,
            "created_at": metric.created_at.isoformat()
        }

    def collect_metric(
        self,
        metric_id: int,
        current_value: float,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Record a new metric measurement

        Args:
            metric_id: Metric to update
            current_value: Current measured value
            timestamp: Measurement timestamp (defaults to now)

        Returns:
            Dict with metric status and breach detection
        """
        metric = self.db.query(models_advanced.SLAMonitoring).filter(
            models_advanced.SLAMonitoring.metric_id == metric_id
        ).first()

        if not metric:
            raise ValueError(f"Metric {metric_id} not found")

        timestamp = timestamp or datetime.utcnow()

        # Calculate deviation and SLA compliance
        deviation_percentage = ((current_value - metric.target_value) / metric.target_value) * 100

        # Determine if within SLA based on metric type
        is_within_sla = self._check_sla_compliance(
            metric.metric_type,
            current_value,
            metric.target_value
        )

        # Update metric
        metric.current_value = current_value
        metric.measurement_timestamp = timestamp
        metric.is_within_sla = is_within_sla
        metric.deviation_percentage = deviation_percentage

        # Check for SLA violation
        violation_created = False
        violation_id = None

        if not is_within_sla:
            # Check if there's an existing open violation
            existing_violation = self.db.query(models_advanced.SLAViolation).filter(
                and_(
                    models_advanced.SLAViolation.metric_id == metric_id,
                    models_advanced.SLAViolation.resolved_at == None
                )
            ).first()

            if not existing_violation:
                # Create new violation
                violation = models_advanced.SLAViolation(
                    metric_id=metric_id,
                    violated_at=timestamp,
                    target_value=metric.target_value,
                    actual_value=current_value,
                    deviation_percentage=deviation_percentage,
                    severity=self._calculate_violation_severity(deviation_percentage),
                    impact_description=f"{metric.metric_name} violated SLA",
                    alert_sent=False
                )
                self.db.add(violation)
                violation_created = True
                violation_id = violation.violation_id
        else:
            # Check if we need to resolve an existing violation
            open_violation = self.db.query(models_advanced.SLAViolation).filter(
                and_(
                    models_advanced.SLAViolation.metric_id == metric_id,
                    models_advanced.SLAViolation.resolved_at == None
                )
            ).first()

            if open_violation:
                open_violation.resolved_at = timestamp
                open_violation.duration_minutes = int((timestamp - open_violation.violated_at).total_seconds() / 60)

        self.db.commit()

        return {
            "metric_id": metric_id,
            "metric_name": metric.metric_name,
            "current_value": current_value,
            "target_value": metric.target_value,
            "target_unit": metric.target_unit,
            "is_within_sla": is_within_sla,
            "deviation_percentage": round(deviation_percentage, 2),
            "violation_created": violation_created,
            "violation_id": violation_id,
            "measured_at": timestamp.isoformat()
        }

    def get_sla_status(
        self,
        vendor_id: Optional[int] = None,
        asset_id: Optional[int] = None
    ) -> Dict:
        """
        Get current SLA status for vendor or asset

        Args:
            vendor_id: Filter by vendor
            asset_id: Filter by asset

        Returns:
            Dict with current SLA metrics and compliance status
        """
        query = self.db.query(models_advanced.SLAMonitoring)

        if vendor_id:
            query = query.filter(models_advanced.SLAMonitoring.vendor_id == vendor_id)
        if asset_id:
            query = query.filter(models_advanced.SLAMonitoring.asset_id == asset_id)

        metrics = query.all()

        if not metrics:
            raise ValueError("No SLA metrics found for specified criteria")

        total_metrics = len(metrics)
        compliant_metrics = sum(1 for m in metrics if m.is_within_sla)
        compliance_rate = (compliant_metrics / total_metrics * 100) if total_metrics > 0 else 0

        metric_details = []
        for m in metrics:
            metric_details.append({
                "metric_id": m.metric_id,
                "metric_name": m.metric_name,
                "metric_type": m.metric_type.value,
                "current_value": m.current_value,
                "target_value": m.target_value,
                "target_unit": m.target_unit,
                "is_within_sla": m.is_within_sla,
                "deviation_percentage": round(m.deviation_percentage, 2) if m.deviation_percentage else None,
                "last_measured": m.measurement_timestamp.isoformat() if m.measurement_timestamp else None
            })

        return {
            "vendor_id": vendor_id,
            "asset_id": asset_id,
            "total_metrics": total_metrics,
            "compliant_metrics": compliant_metrics,
            "non_compliant_metrics": total_metrics - compliant_metrics,
            "compliance_rate": round(compliance_rate, 2),
            "overall_status": "HEALTHY" if compliance_rate >= 95 else "AT_RISK" if compliance_rate >= 80 else "CRITICAL",
            "metrics": metric_details
        }

    def get_violations(
        self,
        metric_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        resolved: Optional[bool] = None,
        lookback_days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get SLA violations with filters

        Args:
            metric_id: Filter by specific metric
            vendor_id: Filter by vendor
            asset_id: Filter by asset
            resolved: Filter by resolution status (None = all)
            lookback_days: Days to look back
            limit: Maximum violations to return

        Returns:
            List of violation records
        """
        query = self.db.query(models_advanced.SLAViolation).join(
            models_advanced.SLAMonitoring,
            models_advanced.SLAViolation.metric_id == models_advanced.SLAMonitoring.metric_id
        )

        # Apply filters
        filters = []

        if metric_id:
            filters.append(models_advanced.SLAViolation.metric_id == metric_id)

        if vendor_id:
            filters.append(models_advanced.SLAMonitoring.vendor_id == vendor_id)

        if asset_id:
            filters.append(models_advanced.SLAMonitoring.asset_id == asset_id)

        if resolved is not None:
            if resolved:
                filters.append(models_advanced.SLAViolation.resolved_at != None)
            else:
                filters.append(models_advanced.SLAViolation.resolved_at == None)

        # Lookback filter
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        filters.append(models_advanced.SLAViolation.violated_at >= cutoff_date)

        if filters:
            query = query.filter(and_(*filters))

        query = query.order_by(models_advanced.SLAViolation.violated_at.desc())
        violations = query.limit(limit).all()

        return [{
            "violation_id": v.violation_id,
            "metric_id": v.metric_id,
            "metric_name": v.metric.metric_name,
            "metric_type": v.metric.metric_type.value,
            "asset_id": v.metric.asset_id,
            "violated_at": v.violated_at.isoformat(),
            "resolved_at": v.resolved_at.isoformat() if v.resolved_at else None,
            "duration_minutes": v.duration_minutes,
            "target_value": v.target_value,
            "actual_value": v.actual_value,
            "deviation_percentage": round(v.deviation_percentage, 2) if v.deviation_percentage else None,
            "severity": v.severity,
            "impact_description": v.impact_description,
            "alert_sent": v.alert_sent,
            "incident_created": v.incident_created,
            "incident_id": v.incident_id
        } for v in violations]

    def get_compliance_trend(
        self,
        metric_id: int,
        days: int = 30
    ) -> Dict:
        """
        Calculate SLA compliance trend over time

        Args:
            metric_id: Metric to analyze
            days: Days to analyze

        Returns:
            Dict with compliance trend and statistics
        """
        metric = self.db.query(models_advanced.SLAMonitoring).filter(
            models_advanced.SLAMonitoring.metric_id == metric_id
        ).first()

        if not metric:
            raise ValueError(f"Metric {metric_id} not found")

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get violations in period
        violations = self.db.query(models_advanced.SLAViolation).filter(
            and_(
                models_advanced.SLAViolation.metric_id == metric_id,
                models_advanced.SLAViolation.violated_at >= cutoff_date
            )
        ).all()

        total_violation_minutes = sum(
            v.duration_minutes for v in violations if v.duration_minutes
        )

        total_minutes_in_period = days * 24 * 60
        uptime_minutes = total_minutes_in_period - total_violation_minutes
        compliance_percentage = (uptime_minutes / total_minutes_in_period) * 100

        # Calculate MTTR (Mean Time To Resolution)
        resolved_violations = [v for v in violations if v.duration_minutes]
        mttr_minutes = statistics.mean([v.duration_minutes for v in resolved_violations]) if resolved_violations else 0

        # Severity breakdown
        severity_counts = {}
        for v in violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        return {
            "metric_id": metric_id,
            "metric_name": metric.metric_name,
            "period_days": days,
            "compliance_percentage": round(compliance_percentage, 4),
            "total_violations": len(violations),
            "total_downtime_minutes": total_violation_minutes,
            "total_downtime_hours": round(total_violation_minutes / 60, 2),
            "mttr_minutes": round(mttr_minutes, 2),
            "mttr_hours": round(mttr_minutes / 60, 2),
            "violations_by_severity": severity_counts,
            "target_value": metric.target_value,
            "target_unit": metric.target_unit,
            "current_status": "COMPLIANT" if metric.is_within_sla else "VIOLATED"
        }

    def collect_from_prometheus(
        self,
        metric_id: int,
        prometheus_url: str,
        query: str
    ) -> Dict:
        """
        Collect metric from Prometheus

        Args:
            metric_id: Metric to update
            prometheus_url: Prometheus server URL
            query: PromQL query

        Returns:
            Dict with collection result
        """
        try:
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if data["status"] != "success":
                raise ValueError(f"Prometheus query failed: {data.get('error', 'Unknown error')}")

            # Extract value from result
            result = data["data"]["result"]
            if not result:
                raise ValueError("No data returned from Prometheus")

            value = float(result[0]["value"][1])

            # Record the metric
            return self.collect_metric(metric_id, value)

        except requests.RequestException as e:
            raise ValueError(f"Failed to connect to Prometheus: {str(e)}")

    def collect_from_cloudwatch(
        self,
        metric_id: int,
        aws_region: str,
        namespace: str,
        metric_name: str,
        dimensions: Dict,
        statistic: str = "Average",
        period_minutes: int = 5
    ) -> Dict:
        """
        Collect metric from AWS CloudWatch

        Args:
            metric_id: Metric to update
            aws_region: AWS region
            namespace: CloudWatch namespace
            metric_name: CloudWatch metric name
            dimensions: Metric dimensions
            statistic: Average, Sum, Minimum, Maximum
            period_minutes: Period in minutes

        Returns:
            Dict with collection result
        """
        try:
            import boto3

            cloudwatch = boto3.client('cloudwatch', region_name=aws_region)

            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=period_minutes)

            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[{"Name": k, "Value": v} for k, v in dimensions.items()],
                StartTime=start_time,
                EndTime=end_time,
                Period=period_minutes * 60,
                Statistics=[statistic]
            )

            if not response['Datapoints']:
                raise ValueError("No data returned from CloudWatch")

            # Get most recent datapoint
            datapoint = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])[-1]
            value = datapoint[statistic]

            return self.collect_metric(metric_id, value)

        except Exception as e:
            raise ValueError(f"Failed to collect from CloudWatch: {str(e)}")

    def _check_sla_compliance(
        self,
        metric_type: models_advanced.SLAMetricType,
        current_value: float,
        target_value: float
    ) -> bool:
        """Check if metric is within SLA based on type"""
        if metric_type in [models_advanced.SLAMetricType.AVAILABILITY, models_advanced.SLAMetricType.RELIABILITY]:
            # Higher is better (e.g., 99.9% availability)
            return current_value >= target_value
        elif metric_type == models_advanced.SLAMetricType.PERFORMANCE:
            # Lower is better (e.g., response time)
            return current_value <= target_value
        elif metric_type == models_advanced.SLAMetricType.FRESHNESS:
            # Lower is better (e.g., data latency)
            return current_value <= target_value
        elif metric_type == models_advanced.SLAMetricType.CAPACITY:
            # Lower is better (e.g., storage utilization)
            return current_value <= target_value
        else:
            return True

    def _calculate_violation_severity(self, deviation_percentage: float) -> str:
        """Calculate violation severity based on deviation"""
        abs_deviation = abs(deviation_percentage)

        if abs_deviation >= 50:
            return "CRITICAL"
        elif abs_deviation >= 25:
            return "HIGH"
        elif abs_deviation >= 10:
            return "MEDIUM"
        else:
            return "LOW"

    def get_sla_statistics(self) -> Dict:
        """Get overall SLA monitoring statistics"""
        total_metrics = self.db.query(models_advanced.SLAMonitoring).count()

        compliant_metrics = self.db.query(models_advanced.SLAMonitoring).filter(
            models_advanced.SLAMonitoring.is_within_sla == True
        ).count()

        # Count by type
        type_counts = self.db.query(
            models_advanced.SLAMonitoring.metric_type,
            func.count(models_advanced.SLAMonitoring.metric_id)
        ).group_by(
            models_advanced.SLAMonitoring.metric_type
        ).all()

        # Active violations
        active_violations = self.db.query(models_advanced.SLAViolation).filter(
            models_advanced.SLAViolation.resolved_at == None
        ).count()

        # Total violations last 30 days
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent_violations = self.db.query(models_advanced.SLAViolation).filter(
            models_advanced.SLAViolation.violated_at >= cutoff
        ).count()

        return {
            "total_metrics": total_metrics,
            "compliant_metrics": compliant_metrics,
            "non_compliant_metrics": total_metrics - compliant_metrics,
            "overall_compliance_rate": round(compliant_metrics / total_metrics * 100, 2) if total_metrics > 0 else None,
            "metrics_by_type": {
                mtype.value: count for mtype, count in type_counts
            },
            "active_violations": active_violations,
            "violations_last_30_days": recent_violations
        }
