"""
Extended SQLAlchemy ORM models for strategic DaaS features
Aligned with DaaS Strategy role requirements
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


# Enums
class InitiativeStatus(enum.Enum):
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"


class VendorStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    EVALUATION = "Evaluation"


class SLAStatus(enum.Enum):
    MET = "Met"
    AT_RISK = "At Risk"
    BREACHED = "Breached"


# Strategic Business Goals
class BusinessGoal(Base):
    __tablename__ = "business_goals"

    goal_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_date = Column(Date)
    status = Column(String(50), default="Active")
    kpi_metric = Column(String(255))  # e.g., "Reduce data access time by 50%"
    current_value = Column(Float)
    target_value = Column(Float)
    priority = Column(String(20))  # High, Medium, Low
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    strategic_initiatives = relationship("StrategicInitiative", back_populates="business_goal")
    asset_alignments = relationship("AssetBusinessAlignment", back_populates="business_goal")


# Strategic Initiatives (DaaS projects)
class StrategicInitiative(Base):
    __tablename__ = "strategic_initiatives"

    initiative_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    initiative_name = Column(String(255), nullable=False)
    description = Column(Text)
    business_goal_id = Column(Integer, ForeignKey("business_goals.goal_id"))
    initiative_lead_id = Column(Integer, ForeignKey("users.user_id"))
    budget_allocated = Column(Float)
    budget_spent = Column(Float, default=0)
    start_date = Column(Date)
    target_date = Column(Date)
    status = Column(String(50), default="Planning")
    expected_roi = Column(Float)  # Expected return on investment
    stakeholder_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business_goal = relationship("BusinessGoal", back_populates="strategic_initiatives")
    deliverables = relationship("InitiativeDeliverable", back_populates="initiative")


# Initiative Deliverables
class InitiativeDeliverable(Base):
    __tablename__ = "initiative_deliverables"

    deliverable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    initiative_id = Column(Integer, ForeignKey("strategic_initiatives.initiative_id"))
    deliverable_name = Column(String(255))
    description = Column(Text)
    due_date = Column(Date)
    status = Column(String(50))
    completion_percentage = Column(Integer, default=0)

    initiative = relationship("StrategicInitiative", back_populates="deliverables")


# Asset to Business Goal Alignment
class AssetBusinessAlignment(Base):
    __tablename__ = "asset_business_alignment"

    alignment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"))
    business_goal_id = Column(Integer, ForeignKey("business_goals.goal_id"))
    contribution_level = Column(String(20))  # Critical, High, Medium, Low
    value_delivered = Column(Text)  # Description of value
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business_goal = relationship("BusinessGoal", back_populates="asset_alignments")


# Vendor Management
class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_name = Column(String(255), nullable=False)
    vendor_type = Column(String(100))  # Cloud Provider, Tool Vendor, Consulting, etc.
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    status = Column(String(50), default="Active")
    contract_start = Column(Date)
    contract_end = Column(Date)
    annual_cost = Column(Float)
    payment_terms = Column(String(100))
    performance_rating = Column(Integer)  # 1-5 stars
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    slas = relationship("VendorSLA", back_populates="vendor")
    assets = relationship("AssetVendorMapping", back_populates="vendor")


# Vendor SLAs
class VendorSLA(Base):
    __tablename__ = "vendor_slas"

    sla_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    sla_metric = Column(String(255))  # e.g., "Uptime", "Response Time"
    target_value = Column(String(100))  # e.g., "99.9%", "< 1 hour"
    current_value = Column(String(100))
    status = Column(String(50))  # Met, At Risk, Breached
    measurement_period = Column(String(50))  # Monthly, Quarterly, Annually
    last_measured = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="slas")


# Asset to Vendor Mapping
class AssetVendorMapping(Base):
    __tablename__ = "asset_vendor_mapping"

    mapping_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"))
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id"))
    service_type = Column(String(100))  # Hosting, Software License, Support, etc.
    monthly_cost = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="assets")


# Business Stakeholders
class Stakeholder(Base):
    __tablename__ = "stakeholders"

    stakeholder_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    department = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    influence_level = Column(String(20))  # Executive, High, Medium, Low
    engagement_level = Column(String(20))  # Champion, Supporter, Neutral, Detractor
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    data_needs = relationship("StakeholderDataNeed", back_populates="stakeholder")


# Stakeholder Data Needs
class StakeholderDataNeed(Base):
    __tablename__ = "stakeholder_data_needs"

    need_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.stakeholder_id"))
    need_description = Column(Text, nullable=False)
    business_justification = Column(Text)
    priority = Column(String(20))  # Critical, High, Medium, Low
    status = Column(String(50))  # Identified, In Progress, Delivered, Deferred
    target_date = Column(Date)
    related_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stakeholder = relationship("Stakeholder", back_populates="data_needs")


# Business Use Cases
class BusinessUseCase(Base):
    __tablename__ = "business_use_cases"

    use_case_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    use_case_name = Column(String(255), nullable=False)
    description = Column(Text)
    business_value = Column(Text)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.stakeholder_id"))
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=True)
    frequency = Column(String(50))  # Daily, Weekly, Monthly, Ad-hoc
    user_count = Column(Integer)
    estimated_value = Column(Float)  # Business value in $
    status = Column(String(50))  # Active, Planned, Deprecated
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Budget Tracking
class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"

    budget_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fiscal_year = Column(Integer, nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.domain_id"))
    category = Column(String(100))  # Infrastructure, Licenses, Personnel, etc.
    allocated_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0)
    forecasted_spend = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
