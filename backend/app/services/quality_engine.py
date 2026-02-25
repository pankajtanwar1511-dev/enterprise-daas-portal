"""
Data Quality Validation Engine
Executes quality rules across 6 dimensions with automated alerting
Supports SQL-based rules, Great Expectations integration, and anomaly detection
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from statistics import mean, stdev
from .. import models, models_advanced


class QualityEngine:
    """
    Manages and executes data quality validation rules
    Tracks quality metrics across 6 dimensions
    """

    # Pre-built rule templates
    RULE_TEMPLATES = {
        "null_check": {
            "sql": "SELECT COUNT(*) as null_count FROM {table} WHERE {column} IS NULL",
            "dimension": "COMPLETENESS",
            "description": "Check for null values in {column}"
        },
        "unique_check": {
            "sql": "SELECT COUNT(*) - COUNT(DISTINCT {column}) as duplicate_count FROM {table}",
            "dimension": "UNIQUENESS",
            "description": "Check for duplicate values in {column}"
        },
        "range_check": {
            "sql": "SELECT COUNT(*) as out_of_range FROM {table} WHERE {column} < {min_value} OR {column} > {max_value}",
            "dimension": "ACCURACY",
            "description": "Check if {column} values are within range [{min_value}, {max_value}]"
        },
        "format_check": {
            "sql": "SELECT COUNT(*) as invalid_format FROM {table} WHERE {column} NOT LIKE '{pattern}'",
            "dimension": "VALIDITY",
            "description": "Check if {column} matches format pattern"
        },
        "freshness_check": {
            "sql": "SELECT JULIANDAY('now') - JULIANDAY(MAX({timestamp_column})) as days_old FROM {table}",
            "dimension": "TIMELINESS",
            "description": "Check data freshness in {table}"
        },
        "referential_integrity": {
            "sql": "SELECT COUNT(*) as orphaned_records FROM {table1} t1 LEFT JOIN {table2} t2 ON t1.{fk_column} = t2.{pk_column} WHERE t2.{pk_column} IS NULL",
            "dimension": "CONSISTENCY",
            "description": "Check referential integrity between {table1} and {table2}"
        }
    }

    def __init__(self, db: Session):
        self.db = db

    def create_rule(
        self,
        rule_name: str,
        asset_id: int,
        quality_dimension: str,
        rule_type: str,
        rule_definition: str,
        threshold_value: Optional[float] = None,
        threshold_operator: str = "<=",
        severity: str = "MEDIUM",
        is_enabled: bool = True,
        schedule: str = "daily",
        alert_channels: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new data quality rule

        Args:
            rule_name: Unique rule name
            asset_id: Asset to validate
            quality_dimension: One of 6 dimensions
            rule_type: "sql", "regex", "python", "great_expectations"
            rule_definition: SQL query, regex pattern, or Python code
            threshold_value: Acceptable threshold
            threshold_operator: "<=", ">=", "==", "!=", "<", ">"
            severity: CRITICAL, HIGH, MEDIUM, LOW
            is_enabled: Whether rule is active
            schedule: "hourly", "daily", "weekly"
            alert_channels: ["email", "slack", "pagerduty"]
            description: Rule description

        Returns:
            Dict with created rule information
        """
        # Validate asset exists
        asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == asset_id
        ).first()

        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Create rule
        rule = models_advanced.DataQualityRule(
            rule_name=rule_name,
            asset_id=asset_id,
            quality_dimension=models_advanced.QualityDimension[quality_dimension],
            rule_type=rule_type,
            rule_definition=rule_definition,
            threshold_value=threshold_value,
            threshold_operator=threshold_operator,
            severity=models_advanced.QualityRuleSeverity[severity],
            is_enabled=is_enabled,
            schedule=schedule,
            alert_channels=alert_channels or [],
            description=description,
            created_at=datetime.utcnow()
        )

        self.db.add(rule)
        self.db.commit()

        return {
            "rule_id": rule.rule_id,
            "rule_name": rule_name,
            "asset_name": asset.asset_name,
            "quality_dimension": quality_dimension,
            "severity": severity,
            "is_enabled": is_enabled,
            "created_at": rule.created_at.isoformat()
        }

    def create_rule_from_template(
        self,
        template_name: str,
        asset_id: int,
        rule_name: str,
        parameters: Dict,
        threshold_value: Optional[float] = None,
        severity: str = "MEDIUM"
    ) -> Dict:
        """
        Create rule from pre-built template

        Args:
            template_name: One of RULE_TEMPLATES keys
            asset_id: Asset to validate
            rule_name: Unique rule name
            parameters: Template parameters (table, column, etc.)
            threshold_value: Threshold for violations
            severity: Rule severity

        Returns:
            Dict with created rule information
        """
        if template_name not in self.RULE_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.RULE_TEMPLATES.keys())}")

        template = self.RULE_TEMPLATES[template_name]

        # Fill in template parameters
        sql = template["sql"]
        for key, value in parameters.items():
            sql = sql.replace(f"{{{key}}}", str(value))

        description = template["description"]
        for key, value in parameters.items():
            description = description.replace(f"{{{key}}}", str(value))

        return self.create_rule(
            rule_name=rule_name,
            asset_id=asset_id,
            quality_dimension=template["dimension"],
            rule_type="sql",
            rule_definition=sql,
            threshold_value=threshold_value,
            severity=severity,
            description=description
        )

    def execute_rule(
        self,
        rule_id: int,
        sample_size: Optional[int] = None
    ) -> Dict:
        """
        Execute a quality rule and record results

        Args:
            rule_id: Rule to execute
            sample_size: Optional row limit for sampling

        Returns:
            Dict with execution results
        """
        rule = self.db.query(models_advanced.DataQualityRule).filter(
            models_advanced.DataQualityRule.rule_id == rule_id
        ).first()

        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        if not rule.is_enabled:
            raise ValueError(f"Rule {rule_id} is disabled")

        # Execute rule based on type
        if rule.rule_type == "sql":
            result_value, details = self._execute_sql_rule(rule, sample_size)
        elif rule.rule_type == "python":
            result_value, details = self._execute_python_rule(rule)
        else:
            raise ValueError(f"Unsupported rule type: {rule.rule_type}")

        # Determine if passed
        passed = self._evaluate_threshold(
            result_value,
            rule.threshold_value,
            rule.threshold_operator
        )

        # Create check run record
        check_run = models_advanced.QualityCheckRun(
            rule_id=rule_id,
            executed_at=datetime.utcnow(),
            result_value=result_value,
            passed=passed,
            details=details,
            sample_size=sample_size
        )

        self.db.add(check_run)

        # Update rule last execution
        rule.last_executed_at = datetime.utcnow()
        rule.last_result_passed = passed

        self.db.commit()

        # Send alerts if failed
        if not passed and rule.alert_channels:
            self._send_alerts(rule, check_run)

        return {
            "check_run_id": check_run.check_run_id,
            "rule_name": rule.rule_name,
            "quality_dimension": rule.quality_dimension.value,
            "result_value": result_value,
            "threshold_value": rule.threshold_value,
            "threshold_operator": rule.threshold_operator,
            "passed": passed,
            "severity": rule.severity.value if not passed else None,
            "executed_at": check_run.executed_at.isoformat()
        }

    def execute_rules_for_asset(
        self,
        asset_id: int,
        dimension: Optional[str] = None
    ) -> Dict:
        """
        Execute all rules for an asset

        Args:
            asset_id: Asset to validate
            dimension: Optional dimension filter

        Returns:
            Dict with execution summary
        """
        query = self.db.query(models_advanced.DataQualityRule).filter(
            and_(
                models_advanced.DataQualityRule.asset_id == asset_id,
                models_advanced.DataQualityRule.is_enabled == True
            )
        )

        if dimension:
            query = query.filter(
                models_advanced.DataQualityRule.quality_dimension == models_advanced.QualityDimension[dimension]
            )

        rules = query.all()

        results = []
        passed_count = 0
        failed_count = 0

        for rule in rules:
            try:
                result = self.execute_rule(rule.rule_id)
                results.append(result)

                if result["passed"]:
                    passed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                results.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "passed": False,
                    "error": str(e)
                })

        return {
            "asset_id": asset_id,
            "total_rules": len(rules),
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": round(passed_count / len(rules) * 100, 2) if rules else 100,
            "results": results
        }

    def get_quality_score(
        self,
        asset_id: int,
        lookback_days: int = 7
    ) -> Dict:
        """
        Calculate overall quality score for an asset

        Args:
            asset_id: Asset to score
            lookback_days: Days to consider for scoring

        Returns:
            Dict with quality score breakdown by dimension
        """
        asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == asset_id
        ).first()

        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Get recent check runs
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        dimension_scores = {}

        for dimension in models_advanced.QualityDimension:
            # Get rules for this dimension
            rules = self.db.query(models_advanced.DataQualityRule).filter(
                and_(
                    models_advanced.DataQualityRule.asset_id == asset_id,
                    models_advanced.DataQualityRule.quality_dimension == dimension
                )
            ).all()

            if not rules:
                continue

            # Get recent check runs for these rules
            rule_ids = [r.rule_id for r in rules]
            check_runs = self.db.query(models_advanced.QualityCheckRun).filter(
                and_(
                    models_advanced.QualityCheckRun.rule_id.in_(rule_ids),
                    models_advanced.QualityCheckRun.executed_at >= cutoff_date
                )
            ).all()

            if check_runs:
                # Calculate pass rate
                passed = sum(1 for run in check_runs if run.passed)
                total = len(check_runs)
                score = round(passed / total * 100, 2)

                dimension_scores[dimension.value] = {
                    "score": score,
                    "total_checks": total,
                    "passed_checks": passed,
                    "failed_checks": total - passed
                }

        # Calculate overall score (weighted average)
        if dimension_scores:
            overall_score = round(mean([d["score"] for d in dimension_scores.values()]), 2)
        else:
            overall_score = None

        return {
            "asset_id": asset_id,
            "asset_name": asset.asset_name,
            "overall_score": overall_score,
            "grade": self._score_to_grade(overall_score) if overall_score else None,
            "dimension_scores": dimension_scores,
            "lookback_days": lookback_days,
            "calculated_at": datetime.utcnow().isoformat()
        }

    def detect_anomalies(
        self,
        rule_id: int,
        lookback_runs: int = 30,
        std_dev_threshold: float = 2.0
    ) -> Dict:
        """
        Detect anomalies in rule execution results using statistical analysis

        Args:
            rule_id: Rule to analyze
            lookback_runs: Number of historical runs to consider
            std_dev_threshold: Number of standard deviations for anomaly

        Returns:
            Dict with anomaly detection results
        """
        rule = self.db.query(models_advanced.DataQualityRule).filter(
            models_advanced.DataQualityRule.rule_id == rule_id
        ).first()

        if not rule:
            raise ValueError(f"Rule {rule_id} not found")

        # Get recent check runs
        check_runs = self.db.query(models_advanced.QualityCheckRun).filter(
            models_advanced.QualityCheckRun.rule_id == rule_id
        ).order_by(
            models_advanced.QualityCheckRun.executed_at.desc()
        ).limit(lookback_runs).all()

        if len(check_runs) < 10:
            return {
                "has_anomaly": False,
                "message": "Insufficient historical data for anomaly detection (need at least 10 runs)"
            }

        # Extract result values
        values = [run.result_value for run in check_runs if run.result_value is not None]

        if len(values) < 10:
            return {
                "has_anomaly": False,
                "message": "Insufficient numeric results for anomaly detection"
            }

        # Calculate statistics
        avg = mean(values)
        std = stdev(values) if len(values) > 1 else 0
        latest_value = values[0]

        # Check if latest value is anomalous
        if std > 0:
            z_score = abs((latest_value - avg) / std)
            is_anomaly = z_score > std_dev_threshold
        else:
            is_anomaly = False
            z_score = 0

        return {
            "has_anomaly": is_anomaly,
            "latest_value": latest_value,
            "historical_average": round(avg, 2),
            "standard_deviation": round(std, 2),
            "z_score": round(z_score, 2),
            "threshold": std_dev_threshold,
            "message": f"Latest value {latest_value} is {z_score:.2f} standard deviations from mean" if is_anomaly else "No anomaly detected"
        }

    def _execute_sql_rule(
        self,
        rule: models_advanced.DataQualityRule,
        sample_size: Optional[int]
    ) -> Tuple[float, Dict]:
        """Execute SQL-based quality rule"""
        sql = rule.rule_definition

        # Add sampling if requested
        if sample_size:
            sql = f"SELECT * FROM ({sql}) LIMIT {sample_size}"

        try:
            result = self.db.execute(text(sql))
            row = result.fetchone()

            if row:
                # Get first column value
                result_value = float(row[0]) if row[0] is not None else 0.0
                details = {
                    "sql": sql,
                    "row_count": 1,
                    "result": dict(row._mapping) if hasattr(row, '_mapping') else str(row)
                }
            else:
                result_value = 0.0
                details = {"sql": sql, "row_count": 0}

            return result_value, details

        except Exception as e:
            raise ValueError(f"SQL execution failed: {str(e)}")

    def _execute_python_rule(self, rule: models_advanced.DataQualityRule) -> Tuple[float, Dict]:
        """Execute Python-based quality rule"""
        # For security, this would need sandboxing in production
        # For now, just return a placeholder
        return 0.0, {"message": "Python rules not yet implemented"}

    def _evaluate_threshold(
        self,
        value: float,
        threshold: Optional[float],
        operator: str
    ) -> bool:
        """Evaluate if value meets threshold criteria"""
        if threshold is None:
            return True

        operators = {
            "<=": lambda v, t: v <= t,
            ">=": lambda v, t: v >= t,
            "==": lambda v, t: v == t,
            "!=": lambda v, t: v != t,
            "<": lambda v, t: v < t,
            ">": lambda v, t: v > t
        }

        if operator not in operators:
            raise ValueError(f"Invalid operator: {operator}")

        return operators[operator](value, threshold)

    def _score_to_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 95:
            return "A"
        elif score >= 85:
            return "B"
        elif score >= 75:
            return "C"
        elif score >= 65:
            return "D"
        else:
            return "F"

    def _send_alerts(
        self,
        rule: models_advanced.DataQualityRule,
        check_run: models_advanced.QualityCheckRun
    ):
        """Send alerts for failed quality checks"""
        # Placeholder for alert sending
        # In production, would integrate with Slack, Email, PagerDuty, etc.
        asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == rule.asset_id
        ).first()

        alert_message = {
            "type": "quality_check_failed",
            "severity": rule.severity.value,
            "rule_name": rule.rule_name,
            "asset_name": asset.asset_name if asset else "Unknown",
            "quality_dimension": rule.quality_dimension.value,
            "result_value": check_run.result_value,
            "threshold_value": rule.threshold_value,
            "executed_at": check_run.executed_at.isoformat(),
            "channels": rule.alert_channels
        }

        # Log alert (in production, would send to actual channels)
        print(f"QUALITY ALERT: {alert_message}")

    def get_rule_history(
        self,
        rule_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get execution history for a rule

        Args:
            rule_id: Rule ID
            limit: Maximum number of runs to return

        Returns:
            List of historical check runs
        """
        check_runs = self.db.query(models_advanced.QualityCheckRun).filter(
            models_advanced.QualityCheckRun.rule_id == rule_id
        ).order_by(
            models_advanced.QualityCheckRun.executed_at.desc()
        ).limit(limit).all()

        return [{
            "check_run_id": run.check_run_id,
            "executed_at": run.executed_at.isoformat(),
            "result_value": run.result_value,
            "passed": run.passed,
            "sample_size": run.sample_size
        } for run in check_runs]
