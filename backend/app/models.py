"""
SQLAlchemy ORM models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    role = relationship("Role", back_populates="users")
    owned_assets = relationship("Asset", foreign_keys="Asset.owner_id", back_populates="owner")
    created_assets = relationship("Asset", foreign_keys="Asset.created_by")


class Domain(Base):
    __tablename__ = "domains"

    domain_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domain_code = Column(String(10), unique=True, nullable=False)
    domain_name = Column(String(100), nullable=False)
    description = Column(Text)
    data_steward_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assets = relationship("Asset", back_populates="domain")


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_name = Column(String(255), unique=True, nullable=False, index=True)
    domain_id = Column(Integer, ForeignKey("domains.domain_id"), nullable=False)
    environment = Column(String(10), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    version = Column(String(20), nullable=False)
    lifecycle_stage = Column(String(20), nullable=False)
    documentation_url = Column(String(500), nullable=True)
    description = Column(Text)
    business_justification = Column(Text)
    tags = Column(Text)  # JSON string
    naming_compliant = Column(Boolean, default=False, index=True)
    compliance_check_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    __table_args__ = (
        CheckConstraint("environment IN ('DEV', 'QA', 'PROD', 'UAT')", name="check_environment"),
        CheckConstraint("lifecycle_stage IN ('Draft', 'Active', 'Deprecated', 'Retired')", name="check_lifecycle"),
    )

    domain = relationship("Domain", back_populates="assets")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_assets")
    lifecycle_history = relationship("LifecycleHistory", back_populates="asset", cascade="all, delete-orphan")
    change_requests = relationship("ChangeRequest", back_populates="asset")
    compliance_violations = relationship("ComplianceViolation", back_populates="asset", cascade="all, delete-orphan")


class LifecycleHistory(Base):
    __tablename__ = "lifecycle_history"

    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(20), nullable=True)
    to_state = Column(String(20), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    change_reason = Column(Text, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    asset = relationship("Asset", back_populates="lifecycle_history")


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    change_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False, index=True)
    change_type = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    impact_assessment = Column(Text)
    rollback_plan = Column(Text)
    requested_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    approval_status = Column(String(20), default="Pending", index=True)
    approver_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_comments = Column(Text)
    implementation_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="Submitted")
    release_version = Column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint("change_type IN ('Modify', 'Deploy', 'Decommission', 'Config')", name="check_change_type"),
        CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="check_risk_level"),
        CheckConstraint("approval_status IN ('Pending', 'Approved', 'Rejected')", name="check_approval_status"),
        CheckConstraint("status IN ('Submitted', 'InProgress', 'Completed', 'RolledBack')", name="check_status"),
    )

    asset = relationship("Asset", back_populates="change_requests")


class ComplianceViolation(Base):
    __tablename__ = "compliance_violations"

    violation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)
    violation_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    resolution_notes = Column(Text)

    __table_args__ = (
        CheckConstraint("severity IN ('Low', 'Medium', 'High')", name="check_severity"),
    )

    asset = relationship("Asset", back_populates="compliance_violations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)


class ComplianceMetric(Base):
    __tablename__ = "compliance_metrics"

    metric_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_assets = Column(Integer, default=0)
    compliant_assets = Column(Integer, default=0)
    compliance_rate = Column(Integer, default=0)
    missing_documentation = Column(Integer, default=0)
    version_conflicts = Column(Integer, default=0)
    pending_changes = Column(Integer, default=0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
