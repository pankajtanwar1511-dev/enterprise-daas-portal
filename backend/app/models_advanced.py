"""
Advanced Data Governance Models
Extends Phase 1 with enterprise-level features:
- Data Lineage Tracking
- Schema Registry
- Data Quality Rules
- Impact Analysis
- Policy Enforcement
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


# ============================================================================
# DATA LINEAGE TRACKING
# ============================================================================

class LineageNodeType(enum.Enum):
    """Types of nodes in data lineage"""
    SOURCE = "source"              # Raw data source (S3, database, API)
    TABLE = "table"                # Database table
    VIEW = "view"                  # Database view
    TRANSFORMATION = "transformation"  # ETL/ELT process
    ANALYTICS = "analytics"        # BI report, dashboard
    API = "api"                    # API endpoint
    FILE = "file"                  # File-based asset
    STREAM = "stream"              # Kafka topic, event stream


class DataLineageNode(Base):
    """
    Represents a node in the data lineage graph
    Each asset can have multiple lineage nodes (one per version/environment)
    """
    __tablename__ = "data_lineage_nodes"

    node_id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)  # Link to asset registry
    node_type = Column(SQLEnum(LineageNodeType), nullable=False)
    node_name = Column(String(500), nullable=False, index=True)
    description = Column(Text)

    # Technical details
    location = Column(String(1000))  # S3 path, database.schema.table, etc.
    schema_definition = Column(JSON)  # Column definitions, types
    row_count = Column(Integer)
    size_bytes = Column(Integer)
    last_updated = Column(DateTime)

    # Metadata
    owner_id = Column(Integer, ForeignKey("users.user_id"))
    domain_id = Column(Integer, ForeignKey("domains.domain_id"))
    tags = Column(JSON)  # Flexible tagging

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", backref="lineage_nodes")
    domain = relationship("Domain", backref="lineage_nodes")
    asset = relationship("Asset", backref="lineage_nodes")

    # Edges - incoming and outgoing
    upstream_edges = relationship("DataLineageEdge", foreign_keys="DataLineageEdge.target_node_id", backref="target_node")
    downstream_edges = relationship("DataLineageEdge", foreign_keys="DataLineageEdge.source_node_id", backref="source_node")


class TransformationType(enum.Enum):
    """Types of data transformations"""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    AGGREGATE = "aggregate"
    JOIN = "join"
    FILTER = "filter"
    ENRICH = "enrich"
    ANONYMIZE = "anonymize"
    CUSTOM = "custom"


class DataLineageEdge(Base):
    """
    Represents a transformation/flow between two lineage nodes
    Forms the directed graph for lineage tracking
    """
    __tablename__ = "data_lineage_edges"

    edge_id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("data_lineage_nodes.node_id"), nullable=False, index=True)
    target_node_id = Column(Integer, ForeignKey("data_lineage_nodes.node_id"), nullable=False, index=True)

    transformation_type = Column(SQLEnum(TransformationType), nullable=False)
    transformation_logic = Column(Text)  # SQL query, script, description
    transformation_tool = Column(String(200))  # dbt, Airflow, Spark, etc.

    # Column-level lineage (optional, for detailed tracking)
    column_mappings = Column(JSON)  # {"source_col": "target_col", ...}

    # Performance metrics
    execution_time_seconds = Column(Float)
    rows_processed = Column(Integer)
    bytes_processed = Column(Integer)

    # Scheduling
    schedule = Column(String(100))  # Cron expression or "on-demand"
    last_run = Column(DateTime)
    next_run = Column(DateTime)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.user_id"))


# ============================================================================
# SCHEMA REGISTRY & VERSION CONTROL
# ============================================================================

class SchemaFormat(enum.Enum):
    """Supported schema formats"""
    AVRO = "avro"
    JSON_SCHEMA = "json_schema"
    PROTOBUF = "protobuf"
    PARQUET = "parquet"
    SQL_DDL = "sql_ddl"


class SchemaCompatibility(enum.Enum):
    """Schema evolution compatibility modes"""
    BACKWARD = "backward"          # New schema can read old data
    FORWARD = "forward"            # Old schema can read new data
    FULL = "full"                  # Both backward and forward
    NONE = "none"                  # Breaking changes allowed


class SchemaRegistry(Base):
    """
    Central schema registry for all data structures
    Supports versioning, compatibility checking, and evolution tracking
    """
    __tablename__ = "schema_registry"

    schema_id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(500), nullable=False, index=True)  # e.g., "customer-events"
    schema_format = Column(SQLEnum(SchemaFormat), nullable=False)
    version = Column(Integer, nullable=False)
    schema_definition = Column(JSON, nullable=False)  # The actual schema

    compatibility_mode = Column(SQLEnum(SchemaCompatibility), default=SchemaCompatibility.BACKWARD)
    is_active = Column(Boolean, default=True)
    is_latest = Column(Boolean, default=True)

    # References
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)
    domain_id = Column(Integer, ForeignKey("domains.domain_id"))

    # Change tracking
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    deprecated_at = Column(DateTime, nullable=True)
    deprecated_reason = Column(Text)

    # Documentation
    description = Column(Text)
    changelog = Column(Text)
    examples = Column(JSON)

    # Relationships
    asset = relationship("Asset", backref="schemas")
    domain = relationship("Domain", backref="schemas")
    creator = relationship("User", backref="schemas_created")


class SchemaValidation(Base):
    """
    Track schema validation results (compatibility checks, etc.)
    """
    __tablename__ = "schema_validations"

    validation_id = Column(Integer, primary_key=True)
    schema_id = Column(Integer, ForeignKey("schema_registry.schema_id"), nullable=False)
    validation_type = Column(String(100))  # "compatibility", "syntax", "breaking_change"
    is_valid = Column(Boolean, nullable=False)
    validation_errors = Column(JSON)  # List of error messages
    validated_at = Column(DateTime, default=datetime.utcnow)
    validated_by = Column(Integer, ForeignKey("users.user_id"))


# ============================================================================
# DATA QUALITY RULES & VALIDATION
# ============================================================================

class QualityDimension(enum.Enum):
    """Data quality dimensions (industry standard)"""
    COMPLETENESS = "completeness"      # % of non-null values
    ACCURACY = "accuracy"              # % matching expected patterns
    CONSISTENCY = "consistency"        # Cross-table integrity
    TIMELINESS = "timeliness"         # Data freshness
    VALIDITY = "validity"             # Format/type correctness
    UNIQUENESS = "uniqueness"         # Duplicate detection


class QualityRuleSeverity(enum.Enum):
    """Severity levels for quality violations"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataQualityRule(Base):
    """
    Data quality validation rules
    Can be SQL-based, regex-based, or custom Python logic
    """
    __tablename__ = "data_quality_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)

    # Target
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)
    table_name = Column(String(200))
    column_name = Column(String(200), nullable=True)  # Column-level or table-level

    # Rule definition
    quality_dimension = Column(SQLEnum(QualityDimension), nullable=False)
    rule_type = Column(String(50))  # "sql", "regex", "python", "great_expectations"
    rule_definition = Column(Text, nullable=False)  # SQL query, regex pattern, etc.

    # Thresholds
    threshold_value = Column(Float)  # Acceptable threshold (e.g., 95% for completeness)
    threshold_operator = Column(String(10))  # ">", "<", ">=", "<=", "==", "!="
    severity = Column(SQLEnum(QualityRuleSeverity), default=QualityRuleSeverity.MEDIUM)

    # Execution
    is_active = Column(Boolean, default=True)
    schedule = Column(String(100))  # Cron expression
    last_run = Column(DateTime)
    next_run = Column(DateTime)

    # Alerting
    alert_on_failure = Column(Boolean, default=True)
    alert_channels = Column(JSON)  # ["email", "slack", "pagerduty"]

    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", backref="quality_rules")
    creator = relationship("User", backref="quality_rules_created")


class QualityCheckRun(Base):
    """
    Execution history of quality rule checks
    """
    __tablename__ = "quality_check_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("data_quality_rules.rule_id"), nullable=False, index=True)

    # Execution
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    execution_time_seconds = Column(Float)

    # Results
    passed = Column(Boolean, nullable=False)
    actual_value = Column(Float)  # Actual metric value
    threshold_value = Column(Float)  # Expected threshold
    violation_count = Column(Integer)
    total_count = Column(Integer)

    # Details
    error_message = Column(Text)
    sample_violations = Column(JSON)  # Sample of failed records

    # Alert
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime)

    # Relationship
    rule = relationship("DataQualityRule", backref="check_runs")


# ============================================================================
# IMPACT ANALYSIS
# ============================================================================

class ImpactAnalysisRun(Base):
    """
    Impact analysis execution results
    What will be affected if we change this asset?
    """
    __tablename__ = "impact_analysis_runs"

    analysis_id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

    # Analysis type
    change_type = Column(String(100))  # "schema_change", "deprecation", "deletion", "policy_change"
    change_description = Column(Text)

    # Results
    impact_score = Column(String(20))  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

    # Dependencies found
    upstream_dependencies_count = Column(Integer, default=0)
    downstream_dependencies_count = Column(Integer, default=0)
    affected_assets = Column(JSON)  # List of affected asset IDs
    affected_pipelines = Column(JSON)  # List of affected pipeline names
    affected_reports = Column(JSON)  # List of affected reports/dashboards
    affected_users_count = Column(Integer, default=0)
    affected_teams = Column(JSON)  # List of affected team names

    # Recommendations
    migration_required = Column(Boolean, default=False)
    estimated_migration_hours = Column(Float)
    recommended_actions = Column(JSON)  # List of recommended steps
    rollback_plan = Column(Text)

    # Execution
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analyzed_by = Column(Integer, ForeignKey("users.user_id"))
    analysis_depth = Column(Integer, default=3)  # How many hops to analyze

    # Relationships
    asset = relationship("Asset", backref="impact_analyses")
    analyzer = relationship("User", backref="impact_analyses_run")


# ============================================================================
# POLICY ENFORCEMENT (CI/CD Integration)
# ============================================================================

class PolicyType(enum.Enum):
    """Types of governance policies"""
    NAMING_CONVENTION = "naming_convention"
    DOCUMENTATION = "documentation"
    OWNERSHIP = "ownership"
    DATA_CLASSIFICATION = "data_classification"
    SLA_REQUIREMENT = "sla_requirement"
    SECURITY_SCAN = "security_scan"
    SCHEMA_VALIDATION = "schema_validation"
    QUALITY_THRESHOLD = "quality_threshold"


class GovernancePolicy(Base):
    """
    Governance policies that can be enforced in CI/CD pipelines
    Policy-as-code approach
    """
    __tablename__ = "governance_policies"

    policy_id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(200), nullable=False, unique=True)
    policy_type = Column(SQLEnum(PolicyType), nullable=False)
    description = Column(Text)

    # Policy definition (executable logic)
    policy_definition = Column(JSON, nullable=False)  # Rules in JSON format

    # Enforcement
    is_blocking = Column(Boolean, default=True)  # Block deployment on failure?
    enforcement_level = Column(String(50))  # "error", "warning", "info"

    # Scope
    applies_to_domains = Column(JSON)  # List of domain IDs or "*" for all
    applies_to_environments = Column(JSON)  # ["PROD", "QA", ...] or "*"

    # Exemptions
    exemption_allowed = Column(Boolean, default=False)
    exemption_requires_approval = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", backref="policies_created")


class PolicyValidation(Base):
    """
    CI/CD policy validation execution results
    """
    __tablename__ = "policy_validations"

    validation_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("governance_policies.policy_id"), nullable=False)

    # Target being validated
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)
    asset_name = Column(String(500))

    # CI/CD context
    pipeline_id = Column(String(200))  # GitHub Actions run ID, Jenkins build number
    commit_sha = Column(String(100))
    branch = Column(String(200))
    triggered_by = Column(String(200))  # Username or automation

    # Results
    passed = Column(Boolean, nullable=False)
    violations = Column(JSON)  # List of violation messages
    deployment_blocked = Column(Boolean, default=False)

    # Exemption handling
    exemption_requested = Column(Boolean, default=False)
    exemption_approved = Column(Boolean, default=False)
    exemption_approver = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    exemption_reason = Column(Text)

    validated_at = Column(DateTime, default=datetime.utcnow)

    policy = relationship("GovernancePolicy", backref="validations")


# ============================================================================
# SLA MONITORING (Real Metrics)
# ============================================================================

class SLAMetricType(enum.Enum):
    """Types of SLA metrics"""
    AVAILABILITY = "availability"      # Uptime %
    PERFORMANCE = "performance"        # Response time, throughput
    RELIABILITY = "reliability"        # Error rate, success rate
    FRESHNESS = "freshness"           # Data latency
    CAPACITY = "capacity"             # Storage, bandwidth utilization


class SLAMonitoring(Base):
    """
    Real-time SLA metric collection and monitoring
    """
    __tablename__ = "sla_monitoring"

    metric_id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)

    metric_type = Column(SQLEnum(SLAMetricType), nullable=False)
    metric_name = Column(String(200), nullable=False)

    # Target SLA
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(50))  # "percent", "milliseconds", "hours", etc.

    # Current measurement
    current_value = Column(Float)
    measurement_timestamp = Column(DateTime, nullable=False, index=True)

    # Status
    is_within_sla = Column(Boolean)
    deviation_percentage = Column(Float)  # How far from target

    # Source
    metric_source = Column(String(100))  # "prometheus", "cloudwatch", "datadog", "manual"
    collection_method = Column(String(100))  # "api", "agent", "webhook"

    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", backref="sla_metrics")
    asset = relationship("Asset", backref="sla_metrics")


class SLAViolation(Base):
    """
    Track SLA breaches for alerting and reporting
    """
    __tablename__ = "sla_violations"

    violation_id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("sla_monitoring.metric_id"), nullable=False)

    # Violation details
    violated_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer)

    target_value = Column(Float)
    actual_value = Column(Float)
    deviation_percentage = Column(Float)

    # Impact
    severity = Column(String(20))  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    impact_description = Column(Text)
    affected_users_count = Column(Integer)

    # Response
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(DateTime)
    incident_created = Column(Boolean, default=False)
    incident_id = Column(String(100))  # Link to incident management system

    # Root cause
    root_cause = Column(Text)
    remediation_actions = Column(Text)

    metric = relationship("SLAMonitoring", backref="violations")
