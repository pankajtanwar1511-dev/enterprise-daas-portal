"""
CRUD Operations for Strategic Management
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from .. import models_extended as models


# Pydantic Schemas
class BusinessGoalCreate(BaseModel):
    goal_name: str
    description: Optional[str] = None
    owner_id: int
    target_date: Optional[date] = None
    status: str = "Active"
    kpi_metric: Optional[str] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    priority: Optional[str] = "Medium"
    success_criteria: Optional[str] = None
    expected_roi: Optional[float] = None
    investment_amount: Optional[float] = None
    completion_percentage: Optional[int] = 0


class BusinessGoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    kpi_metric: Optional[str] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    priority: Optional[str] = None
    success_criteria: Optional[str] = None
    expected_roi: Optional[float] = None
    investment_amount: Optional[float] = None
    completion_percentage: Optional[int] = None


class StrategicInitiativeCreate(BaseModel):
    initiative_name: str
    description: Optional[str] = None
    business_goal_id: Optional[int] = None  # Alias field
    goal_id: Optional[int] = None  # Accept both names
    initiative_lead_id: Optional[int] = None  # Alias field
    owner_id: Optional[int] = None  # Accept both names
    budget_allocated: Optional[float] = None
    budget_spent: Optional[float] = 0.0
    actual_spend: Optional[float] = None  # Alias for budget_spent
    start_date: Optional[date] = None
    target_date: Optional[date] = None  # Alias field
    target_completion_date: Optional[date] = None  # Accept both names
    status: str = "Planning"
    expected_roi: Optional[float] = None
    stakeholder_count: int = 0
    completion_percentage: Optional[int] = 0


class StrategicInitiativeUpdate(BaseModel):
    initiative_name: Optional[str] = None
    description: Optional[str] = None
    business_goal_id: Optional[int] = None
    goal_id: Optional[int] = None
    initiative_lead_id: Optional[int] = None
    owner_id: Optional[int] = None
    budget_allocated: Optional[float] = None
    budget_spent: Optional[float] = None
    actual_spend: Optional[float] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    status: Optional[str] = None
    expected_roi: Optional[float] = None
    stakeholder_count: Optional[int] = None
    completion_percentage: Optional[int] = None


# Business Goals CRUD
def create_business_goal(goal_data: BusinessGoalCreate, db: Session):
    """Create a new business goal"""
    new_goal = models.BusinessGoal(**goal_data.model_dump())
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


def get_business_goal(goal_id: int, db: Session):
    """Get business goal by ID"""
    goal = db.query(models.BusinessGoal).filter(models.BusinessGoal.goal_id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Business goal not found")
    return goal


def update_business_goal(goal_id: int, goal_update: BusinessGoalUpdate, db: Session):
    """Update business goal"""
    goal = get_business_goal(goal_id, db)

    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


def delete_business_goal(goal_id: int, db: Session):
    """Delete business goal"""
    goal = get_business_goal(goal_id, db)
    db.delete(goal)
    db.commit()
    return None


# Strategic Initiatives CRUD
def create_strategic_initiative(initiative_data: StrategicInitiativeCreate, db: Session):
    """Create a new strategic initiative"""
    # Convert to dict and handle alias fields
    data_dict = initiative_data.model_dump(exclude_unset=True)

    # Map alias fields to model fields
    if "goal_id" in data_dict and "business_goal_id" not in data_dict:
        data_dict["business_goal_id"] = data_dict.pop("goal_id")
    elif "goal_id" in data_dict:
        # If both exist, remove goal_id as business_goal_id takes precedence
        data_dict.pop("goal_id")

    if "owner_id" in data_dict and "initiative_lead_id" not in data_dict:
        data_dict["initiative_lead_id"] = data_dict.pop("owner_id")
    elif "owner_id" in data_dict:
        data_dict.pop("owner_id")

    if "actual_spend" in data_dict and "budget_spent" not in data_dict:
        data_dict["budget_spent"] = data_dict.pop("actual_spend")
    elif "actual_spend" in data_dict:
        data_dict.pop("actual_spend")

    if "target_completion_date" in data_dict and "target_date" not in data_dict:
        data_dict["target_date"] = data_dict.pop("target_completion_date")
    elif "target_completion_date" in data_dict:
        data_dict.pop("target_completion_date")

    # Remove fields not in the model
    data_dict.pop("completion_percentage", None)  # Not in model

    new_initiative = models.StrategicInitiative(**data_dict)
    db.add(new_initiative)
    db.commit()
    db.refresh(new_initiative)
    return new_initiative


def get_strategic_initiative(initiative_id: int, db: Session):
    """Get strategic initiative by ID"""
    initiative = db.query(models.StrategicInitiative).filter(
        models.StrategicInitiative.initiative_id == initiative_id
    ).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="Strategic initiative not found")
    return initiative


def update_strategic_initiative(initiative_id: int, initiative_update: StrategicInitiativeUpdate, db: Session):
    """Update strategic initiative"""
    initiative = get_strategic_initiative(initiative_id, db)

    update_data = initiative_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(initiative, field, value)

    db.commit()
    db.refresh(initiative)
    return initiative


def delete_strategic_initiative(initiative_id: int, db: Session):
    """Delete strategic initiative"""
    initiative = get_strategic_initiative(initiative_id, db)
    db.delete(initiative)
    db.commit()
    return None


# Value Delivered Metrics Schemas
class ValueDeliveredMetricCreate(BaseModel):
    domain_id: int
    initiative_id: Optional[int] = None
    business_goal_id: Optional[int] = None
    metric_type: Optional[str] = None  # cost_savings, time_reduction, revenue_increase, efficiency_gain, quality_improvement
    value_delivered: str
    key_achievement: str
    measurement_date: date
    measurement_period: Optional[str] = None  # Annual, Quarterly, Monthly, One-time
    data_source: Optional[str] = "manual"  # manual, calculated, integrated, system_generated
    validated_by: Optional[int] = None
    validation_date: Optional[date] = None
    status: str = "Draft"  # Draft, Approved, Published, Archived
    is_active: bool = True
    display_order: int = 0
    created_by: int
    notes: Optional[str] = None


class ValueDeliveredMetricUpdate(BaseModel):
    domain_id: Optional[int] = None
    initiative_id: Optional[int] = None
    business_goal_id: Optional[int] = None
    metric_type: Optional[str] = None
    value_delivered: Optional[str] = None
    key_achievement: Optional[str] = None
    measurement_date: Optional[date] = None
    measurement_period: Optional[str] = None
    data_source: Optional[str] = None
    validated_by: Optional[int] = None
    validation_date: Optional[date] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    notes: Optional[str] = None


# Value Delivered Metrics CRUD
def create_value_metric(metric_data: ValueDeliveredMetricCreate, db: Session):
    """Create a new value delivered metric"""
    new_metric = models.ValueDeliveredMetric(**metric_data.model_dump())
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric


def get_value_metric(metric_id: int, db: Session):
    """Get value delivered metric by ID"""
    metric = db.query(models.ValueDeliveredMetric).filter(
        models.ValueDeliveredMetric.metric_id == metric_id
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Value delivered metric not found")
    return metric


def update_value_metric(metric_id: int, metric_update: ValueDeliveredMetricUpdate, db: Session):
    """Update value delivered metric"""
    metric = get_value_metric(metric_id, db)

    update_data = metric_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(metric, field, value)

    db.commit()
    db.refresh(metric)
    return metric


def delete_value_metric(metric_id: int, db: Session):
    """Delete value delivered metric"""
    metric = get_value_metric(metric_id, db)
    db.delete(metric)
    db.commit()
    return None
